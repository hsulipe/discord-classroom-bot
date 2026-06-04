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
        member = guild.get_member(mid)
        name = (member.display_name if member else f"<id:{mid}>")[:23]
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
    bot.run(DISCORD_TOKEN)
