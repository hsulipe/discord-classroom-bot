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


async def apply_registration(member: discord.Member, real_name: str) -> None:
    try:
        await member.edit(nick=real_name)
    except discord.Forbidden:
        logger.warning("Could not set nickname for %s (id=%s) — insufficient permissions", member, member.id)
    if MEMBER_ROLE_NAME:
        role = discord.utils.get(member.guild.roles, name=MEMBER_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                logger.warning("Could not assign role %r to %s (id=%s) — check role hierarchy", MEMBER_ROLE_NAME, member, member.id)
        else:
            logger.warning("Member role %r not found in guild %s", MEMBER_ROLE_NAME, member.guild.name)


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
                await pc.message.edit(content="Presence check closed.", view=pc.view)
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

    lines = [
        "**Attendance Report**",
        f"Start  : {session.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"End    : {end.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Duration: {h}h {m}m {s}s",
        f"Total students: {len(member_ids)}",
        "",
    ]

    if not member_ids:
        lines.append("No students attended.")
        return "\n".join(lines)

    lines.append("```")
    lines.append(f"{'Name':<24} {'Time in session':<18} Presence")
    lines.append("-" * 60)

    for mid in member_ids:
        name = resolve_name(mid, guild)[:23]
        secs = int(member_time.get(mid, 0))
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        time_str = f"{hh}h {mm}m {ss}s" if hh else f"{mm}m {ss}s"
        status = "Confirmed present" if mid in all_signatories else "Joined only"
        lines.append(f"{name:<24} {time_str:<18} {status}")

    lines.append("```")
    return "\n".join(lines)


@bot.event
async def on_ready():
    logger.info("Logged in as %s (id=%s)", bot.user, bot.user.id)


@bot.event
async def on_member_join(member: discord.Member) -> None:
    welcome_text = (
        f"Welcome {member.mention}! "
        "Please register your real name so the teacher can identify you in attendance reports."
    )
    if WELCOME_CHANNEL_ID:
        channel = bot.get_channel(int(WELCOME_CHANNEL_ID))
        if channel:
            msg = await channel.send(welcome_text, view=RegistrationView())
            welcome_messages[member.id] = msg
            return
        logger.warning("Welcome channel id=%s not found, falling back to DM", WELCOME_CHANNEL_ID)
    try:
        await member.send(welcome_text, view=RegistrationView())
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


class RegistrationModal(discord.ui.Modal, title="Register Your Name"):
    full_name = discord.ui.TextInput(
        label="Full Name",
        placeholder="e.g. John Silva",
        min_length=2,
        max_length=80,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        real_name = self.full_name.value.strip()
        names[str(interaction.user.id)] = real_name
        save_names()
        await interaction.response.send_message(
            f"Name registered as **{real_name}**. It will appear in attendance reports.",
            ephemeral=True,
        )
        await apply_registration(interaction.user, real_name)
        msg = welcome_messages.pop(interaction.user.id, None)
        if msg:
            try:
                await msg.edit(content=f"✅ **{real_name}** has registered.", view=None)
            except discord.HTTPException:
                pass


class RegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Set My Name", style=discord.ButtonStyle.primary)
    async def set_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistrationModal())


class PresenceView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Sign Presence", style=discord.ButtonStyle.green, emoji="✅")
    async def sign_presence(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = sessions.get(self.guild_id)
        if not session or not session.active_presence or not session.active_presence.open:
            await interaction.response.send_message("No open presence check.", ephemeral=True)
            return
        user_id = interaction.user.id
        if user_id in session.active_presence.signatories:
            await interaction.response.send_message("You already signed presence.", ephemeral=True)
            return
        session.active_presence.signatories.add(user_id)
        await interaction.response.send_message("Presence signed!", ephemeral=True)


@bot.command(name="register")
async def cmd_register(ctx: commands.Context, *, full_name: str = ""):
    real_name = full_name.strip()
    if not real_name:
        await ctx.send("Usage: `!register Your Full Name`")
        return
    names[str(ctx.author.id)] = real_name
    save_names()
    await apply_registration(ctx.author, real_name)
    await ctx.send(f"Registered as **{real_name}**. This name will appear in attendance reports.")


@bot.command(name="setname")
async def cmd_setname(ctx: commands.Context, member: discord.Member = None, *, full_name: str = ""):
    if not is_teacher(ctx.author):
        await ctx.send("Permission denied: Teacher role required.")
        return
    if member is None or not full_name.strip():
        await ctx.send("Usage: `!setname @member Their Full Name`")
        return
    real_name = full_name.strip()
    names[str(member.id)] = real_name
    save_names()
    await apply_registration(member, real_name)
    await ctx.send(f"Set **{member.display_name}**'s attendance name to **{real_name}**.")
    try:
        await member.send(
            f"Your attendance name has been set to **{real_name}** by the teacher."
        )
    except discord.Forbidden:
        pass


@bot.command(name="start")
async def cmd_start(ctx: commands.Context):
    if not is_teacher(ctx.author):
        await ctx.send("Permission denied: Teacher role required.")
        return
    session = sessions.get(ctx.guild.id)
    if session and session.active:
        await ctx.send("A class is already in progress. Use `!endclass` first.")
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("You must be in a voice channel to start a class.")
        return

    channel = ctx.author.voice.channel
    now = datetime.now(timezone.utc)
    new_session = SessionState(
        voice_channel_id=channel.id,
        teacher_id=ctx.author.id,
        start_time=now,
    )

    # Record members already present in channel (task 6.1)
    for member in channel.members:
        if member.id != ctx.author.id:
            new_session.join_leave_log.append({"type": "join", "member_id": member.id, "timestamp": now})

    sessions[ctx.guild.id] = new_session
    count = len(channel.members) - 1
    await ctx.send(
        f"Class started in **{channel.name}**. "
        f"Tracking attendance ({count} student(s) already present)."
    )


@bot.command(name="endclass")
async def cmd_endclass(ctx: commands.Context):
    if not is_teacher(ctx.author):
        await ctx.send("Permission denied: Teacher role required.")
        return
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("No class is in progress.")
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
        await ctx.send(f"Class ended. Report posted to {report_channel.mention}.")
    else:
        logger.error("Report channel not found or not configured (REPORT_CHANNEL_ID=%s)", REPORT_CHANNEL_ID)
        await ctx.send(
            "Class ended, but the report channel is misconfigured "
            f"(REPORT_CHANNEL_ID={REPORT_CHANNEL_ID!r}). Report:\n{report}"
        )


@bot.command(name="presence")
async def cmd_presence(ctx: commands.Context):
    if not is_teacher(ctx.author):
        await ctx.send("Permission denied: Teacher role required.")
        return
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("No active class session.")
        return

    await close_presence(session)  # close any prior check

    view = PresenceView(ctx.guild.id)
    msg = await ctx.send(
        "Presence check open! Click the button or type `!present`.",
        view=view,
    )

    pc = PresenceCheck(message=msg, view=view)
    session.active_presence = pc


@bot.command(name="present")
async def cmd_present(ctx: commands.Context):
    session = sessions.get(ctx.guild.id)
    if not session or not session.active:
        await ctx.send("No active class session.")
        return
    if not session.active_presence or not session.active_presence.open:
        await ctx.send("No open presence check right now.")
        return
    user_id = ctx.author.id
    if user_id in session.active_presence.signatories:
        await ctx.send("You already signed presence.")
        return
    session.active_presence.signatories.add(user_id)
    await ctx.send(f"{ctx.author.display_name} signed presence. ✅")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in environment.")
    load_names()
    bot.run(DISCORD_TOKEN)
