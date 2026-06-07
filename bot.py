import json
import os
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
REPORT_CHANNEL_ID = os.getenv("REPORT_CHANNEL_ID")
TEACHER_ROLE_NAME = os.getenv("TEACHER_ROLE_NAME", "Teacher")
WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID")
MEMBER_ROLE_NAME = os.getenv("MEMBER_ROLE_NAME")
NAMES_FILE = "names.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@dataclass
class PresenceCheck:
    signatories: set = field(default_factory=set)
    open: bool = True
    message: Optional[discord.Message] = None
    view: Optional["PresenceView"] = None


@dataclass
class SessionState:
    active: bool = True
    voice_channel_id: int = 0
    teacher_id: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    class_name: str = ""
    join_leave_log: list = field(default_factory=list)
    presence_checks: list = field(default_factory=list)
    active_presence: Optional[PresenceCheck] = None


# Per-guild session registry
sessions: dict[int, SessionState] = {}

# Real-name registry: member_id (str) -> real name
names: dict[str, str] = {}

# Pending welcome messages: member_id -> Message (cleared after registration)
welcome_messages: dict[int, discord.Message] = {}


def load_names() -> None:
    global names
    if os.path.exists(NAMES_FILE):
        try:
            with open(NAMES_FILE, "r", encoding="utf-8") as f:
                names = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load %s: %s", NAMES_FILE, exc)


def save_names() -> None:
    tmp = NAMES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)
    os.replace(tmp, NAMES_FILE)


async def apply_registration(member: discord.Member, real_name: str) -> list[str]:
    """Applies nickname and role after registration. Returns a list of human-readable failure descriptions."""
    issues: list[str] = []
    try:
        await member.edit(nick=real_name)
    except discord.Forbidden:
        logger.warning("Could not set nickname for %s (id=%s)", member, member.id)
        issues.append("apelido — o bot precisa da permissão **Gerenciar Apelidos** e seu cargo deve estar acima do seu em Configurações do Servidor → Cargos")
    if MEMBER_ROLE_NAME:
        role = discord.utils.get(member.guild.roles, name=MEMBER_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                logger.warning("Could not assign role %r to %s (id=%s)", MEMBER_ROLE_NAME, member, member.id)
                issues.append(f"cargo **{MEMBER_ROLE_NAME}** — o cargo do bot deve estar acima de **{MEMBER_ROLE_NAME}** em Configurações do Servidor → Cargos")
        else:
            logger.warning("Member role %r not found in guild %s", MEMBER_ROLE_NAME, member.guild.name)
            issues.append(f"cargo **{MEMBER_ROLE_NAME}** — cargo não encontrado, verifique `MEMBER_ROLE_NAME` no `.env`")
    return issues


def is_teacher(member: discord.Member) -> bool:
    return any(r.name == TEACHER_ROLE_NAME for r in member.roles)


async def close_presence(session: SessionState) -> None:
    pc = session.active_presence
    if not pc or not pc.open:
        return
    pc.open = False
    if pc.view:
        for item in pc.view.children:
            item.disabled = True
        if pc.message:
            try:
                await pc.message.edit(content="Verificação de presença encerrada.", view=pc.view)
            except discord.HTTPException as exc:
                logger.warning("Could not edit presence message: %s", exc)
    session.presence_checks.append(pc)
    session.active_presence = None


def resolve_name(member_id: int, guild: discord.Guild) -> str:
    if str(member_id) in names:
        return names[str(member_id)]
    member = guild.get_member(member_id)
    return member.display_name if member else f"<id:{member_id}>"


def build_report(session: SessionState, guild: discord.Guild) -> str:
    end = session.end_time or datetime.now(timezone.utc)
    duration = end - session.start_time
    total_secs = int(duration.total_seconds())
    h, rem = divmod(total_secs, 3600)
    m, s = divmod(rem, 60)

    all_signatories: set[int] = set()
    for pc in session.presence_checks:
        all_signatories.update(pc.signatories)

    # Compute per-member time from join/leave log
    member_ids: set[int] = {e["member_id"] for e in session.join_leave_log}
    last_join: dict[int, datetime] = {}
    member_time: dict[int, float] = {}

    for event in session.join_leave_log:
        mid = event["member_id"]
        ts: datetime = event["timestamp"]
        if event["type"] == "join":
            last_join[mid] = ts
        elif event["type"] == "leave" and mid in last_join:
            member_time[mid] = member_time.get(mid, 0.0) + (ts - last_join.pop(mid)).total_seconds()

    # Members still in channel at end
    for mid, join_ts in last_join.items():
        member_time[mid] = member_time.get(mid, 0.0) + (end - join_ts).total_seconds()

    lines = ["**Relatório de Presença**"]
    if session.class_name:
        lines.append(f"Turma  : {session.class_name}")
    lines += [
        f"Início : {session.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Fim    : {end.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Duração: {h}h {m}m {s}s",
        f"Total de alunos: {len(member_ids)}",
        "",
    ]

    if not member_ids:
        lines.append("Nenhum aluno participou.")
        return "\n".join(lines)

    lines.append("```")
    lines.append(f"{'Nome':<24} {'Tempo na aula':<18} Presença")
    lines.append("-" * 60)

    for mid in member_ids:
        name = resolve_name(mid, guild)[:23]
        secs = int(member_time.get(mid, 0))
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        time_str = f"{hh}h {mm}m {ss}s" if hh else f"{mm}m {ss}s"
        status = "Presença confirmada" if mid in all_signatories else "Apenas entrou"
        lines.append(f"{name:<24} {time_str:<18} {status}")

    lines.append("```")
    return "\n".join(lines)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (id=%s)", bot.user, bot.user.id)


@bot.event
async def on_member_join(member: discord.Member) -> None:
    if WELCOME_CHANNEL_ID:
        channel = bot.get_channel(int(WELCOME_CHANNEL_ID))
        if channel:
            await channel.send(f"Bem-vindo(a) {member.mention}! Verifique seu tópico privado para concluir o cadastro.")
            thread = await channel.create_thread(
                name=f"Welcome {member.display_name}",
                type=discord.ChannelType.private_thread,
                invitable=False,
            )
            await thread.add_user(member)
            await thread.send(
                f"Olá {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença.",
                view=RegistrationView(thread=thread),
            )
            return
        logger.warning("Welcome channel id=%s not found, falling back to DM", WELCOME_CHANNEL_ID)
    try:
        await member.send(
            f"Bem-vindo(a) {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença.",
            view=RegistrationView(),
        )
    except discord.Forbidden:
        logger.warning("Could not DM %s (id=%s) — DMs disabled", member, member.id)


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
) -> None:
    session = sessions.get(member.guild.id)
    if not session or not session.active:
        return
    if member.id == session.teacher_id:
        return

    now = datetime.now(timezone.utc)
    tracked = session.voice_channel_id

    joined = after.channel and after.channel.id == tracked and (not before.channel or before.channel.id != tracked)
    left = before.channel and before.channel.id == tracked and (not after.channel or after.channel.id != tracked)

    if joined:
        session.join_leave_log.append({"type": "join", "member_id": member.id, "timestamp": now})
    elif left:
        session.join_leave_log.append({"type": "leave", "member_id": member.id, "timestamp": now})


class RegistrationModal(discord.ui.Modal, title="Cadastre seu Nome"):
    full_name = discord.ui.TextInput(
        label="Nome Completo",
        placeholder="ex.: João Silva",
        min_length=2,
        max_length=80,
    )

    def __init__(self, thread: Optional[discord.Thread] = None):
        super().__init__()
        self.thread = thread

    async def on_submit(self, interaction: discord.Interaction) -> None:
        real_name = self.full_name.value.strip()
        names[str(interaction.user.id)] = real_name
        save_names()
        await interaction.response.send_message(
            f"Nome cadastrado como **{real_name}**. Ele aparecerá nos relatórios de presença.",
            ephemeral=True,
        )
        # interaction.user may be discord.User (not Member) in some contexts; resolve from guild
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        if member:
            issues = await apply_registration(member, real_name)
            if issues:
                await interaction.followup.send(
                    f"⚠️ Nome salvo, mas os itens a seguir não puderam ser aplicados:\n"
                    + "\n".join(f"• {i}" for i in issues),
                    ephemeral=True,
                )
        msg = welcome_messages.pop(interaction.user.id, None)
        if msg:
            try:
                await msg.edit(content=f"✅ **{real_name}** realizou o cadastro.", view=None)
            except discord.HTTPException:
                pass
        if self.thread:
            try:
                await self.thread.edit(archived=True)
            except discord.HTTPException:
                logger.warning("Could not archive registration thread id=%s", self.thread.id)


class RegistrationView(discord.ui.View):
    def __init__(self, thread: Optional[discord.Thread] = None):
        super().__init__(timeout=None)
        self.thread = thread

    @discord.ui.button(label="Definir Meu Nome", style=discord.ButtonStyle.primary)
    async def set_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistrationModal(thread=self.thread))


class PresenceView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Assinar Presença", style=discord.ButtonStyle.green, emoji="✅")
    async def sign_presence(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = sessions.get(self.guild_id)
        if not session or not session.active_presence or not session.active_presence.open:
            await interaction.response.send_message("Nenhuma verificação de presença aberta.", ephemeral=True)
            return
        user_id = interaction.user.id
        if user_id in session.active_presence.signatories:
            await interaction.response.send_message("Você já assinou a presença.", ephemeral=True)
            return
        session.active_presence.signatories.add(user_id)
        await interaction.response.send_message("Presença assinada!", ephemeral=True)


@bot.command(name="register")
async def cmd_register(ctx: commands.Context, *, full_name: str = ""):
    real_name = full_name.strip()
    if not real_name:
        await ctx.send("Uso: `!register Seu Nome Completo`")
        return
    names[str(ctx.author.id)] = real_name
    save_names()
    issues = await apply_registration(ctx.author, real_name)
    if issues:
        await ctx.send(
            f"Nome salvo como **{real_name}**, mas os itens a seguir não puderam ser aplicados:\n"
            + "\n".join(f"• {i}" for i in issues)
        )
    else:
        await ctx.send(f"Cadastrado como **{real_name}**. Apelido e cargo atualizados.")


@bot.command(name="setname")
async def cmd_setname(ctx: commands.Context, member: discord.Member = None, *, full_name: str = ""):
    if not is_teacher(ctx.author):
        await ctx.send("Permissão negada: cargo de Professor necessário.")
        return
    if member is None or not full_name.strip():
        await ctx.send("Uso: `!setname @membro Nome Completo`")
        return
    real_name = full_name.strip()
    names[str(member.id)] = real_name
    save_names()
    issues = await apply_registration(member, real_name)
    if issues:
        await ctx.send(
            f"Nome salvo como **{real_name}** para {member.mention}, mas os itens a seguir não puderam ser aplicados:\n"
            + "\n".join(f"• {i}" for i in issues)
        )
    else:
        await ctx.send(f"Nome de {member.mention} definido como **{real_name}**, apelido e cargo atualizados.")


@cmd_setname.error
async def cmd_setname_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send(
            f"Membro `{error.argument}` não encontrado. "
            "Use uma menção válida do Discord: digite `!setname ` seguido de **@** e clique no nome do membro na lista de autocompletar."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Uso: `!setname @membro Nome Completo`")
    else:
        raise error
    try:
        await member.send(
            f"Seu nome para presença foi definido como **{real_name}** pelo professor."
        )
    except discord.Forbidden:
        pass


@bot.command(name="start")
async def cmd_start(ctx: commands.Context, *, class_name: str = ""):
    if not is_teacher(ctx.author):
        await ctx.send("Permissão negada: cargo de Professor necessário.")
        return
    session = sessions.get(ctx.guild.id)
    if session and session.active:
        await ctx.send("Já há uma aula em andamento. Use `!endclass` primeiro.")
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("Você precisa estar em um canal de voz para iniciar uma aula.")
        return

    channel = ctx.author.voice.channel
    now = datetime.now(timezone.utc)
    new_session = SessionState(
        voice_channel_id=channel.id,
        teacher_id=ctx.author.id,
        start_time=now,
        class_name=class_name.strip(),
    )

    for member in channel.members:
        if member.id != ctx.author.id:
            new_session.join_leave_log.append({"type": "join", "member_id": member.id, "timestamp": now})

    sessions[ctx.guild.id] = new_session
    count = len(channel.members) - 1
    label = f'Aula "{new_session.class_name}" iniciada' if new_session.class_name else "Aula iniciada"
    await ctx.send(
        f"{label} em **{channel.name}**. "
        f"Monitorando presença ({count} aluno(s) já presente(s))."
    )


@bot.command(name="endclass")
async def cmd_endclass(ctx: commands.Context):
    if not is_teacher(ctx.author):
        await ctx.send("Permissão negada: cargo de Professor necessário.")
        return
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("Nenhuma aula em andamento.")
        return

    session.active = False
    session.end_time = datetime.now(timezone.utc)

    await close_presence(session)  # task 6.2: safe even if no presence open

    report = build_report(session, ctx.guild)
    del sessions[ctx.guild.id]

    report_channel: Optional[discord.TextChannel] = None
    if REPORT_CHANNEL_ID:
        try:
            report_channel = bot.get_channel(int(REPORT_CHANNEL_ID))
        except (ValueError, TypeError):
            pass

    if report_channel:
        await report_channel.send(report)
        await ctx.send(f"Aula encerrada. Relatório enviado para {report_channel.mention}.")
    else:
        logger.error("Report channel not found or not configured (REPORT_CHANNEL_ID=%s)", REPORT_CHANNEL_ID)
        await ctx.send(
            "Aula encerrada, mas o canal de relatório está mal configurado "
            f"(REPORT_CHANNEL_ID={REPORT_CHANNEL_ID!r}). Relatório:\n{report}"
        )


@bot.command(name="presence")
async def cmd_presence(ctx: commands.Context):
    if not is_teacher(ctx.author):
        await ctx.send("Permissão negada: cargo de Professor necessário.")
        return
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("Nenhuma aula ativa no momento.")
        return

    await close_presence(session)  # close any prior check

    view = PresenceView(ctx.guild.id)
    msg = await ctx.send(
        "Verificação de presença aberta! Clique no botão ou digite `!present`.",
        view=view,
    )

    pc = PresenceCheck(message=msg, view=view)
    session.active_presence = pc


@bot.command(name="present")
async def cmd_present(ctx: commands.Context):
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("Nenhuma aula ativa no momento.")
        return
    if not session.active_presence or not session.active_presence.open:
        await ctx.send("Nenhuma verificação de presença aberta no momento.")
        return
    user_id = ctx.author.id
    if user_id in session.active_presence.signatories:
        await ctx.send("Você já assinou a presença.")
        return
    session.active_presence.signatories.add(user_id)
    await ctx.send(f"{ctx.author.display_name} assinou a presença. ✅")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in environment.")
    load_names()
    bot.run(DISCORD_TOKEN)
