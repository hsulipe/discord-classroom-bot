## Context

Fresh Discord bot project with no existing code. Two actor roles: **teacher** (controls class lifecycle) and **student** (signs attendance). Bot must track who joins/leaves a voice channel and verify active presence on demand. State is ephemeral per class session; no persistent DB required for MVP.

## Goals / Non-Goals

**Goals:**
- Track join/leave events for a single active class session per guild
- Allow mid-class presence checks with button + command sign-in
- Generate and post a structured attendance report on `!endclass`
- Prevent duplicate presence signatures
- Support one concurrent class per guild

**Non-Goals:**
- Multi-classroom support per guild (single active session)
- Persistent historical records (report is posted to channel, not stored)
- Grade integration or LMS sync
- Slash command migration (prefix commands only for MVP)

## Decisions

### Language & Framework: Python + discord.py
discord.py has first-class support for prefix commands (`commands.Bot`), button interactions (`discord.ui.View`), and voice state events. Mature, well-documented. Alternative: discord.js (Node) — rejected to avoid JS toolchain for a simple bot.

### State: In-memory per guild
Session state (class active flag, join/leave log, presence signatories) held in a Python dict keyed by guild ID. Resets on `!endclass`. No DB dependency for MVP.
- Risk: state lost on bot restart mid-class. Acceptable for MVP.

### Role enforcement: Discord role names
Teacher vs. student distinguished by Discord role assignment. Bot checks `ctx.author.roles` for a configured teacher role name (default: `"Teacher"`). Avoids hardcoding user IDs.

### Presence button: `discord.ui.View` with timeout
`!presence` sends a message with a persistent `View` containing a "Sign Presence" button. View stored in session state so `!endclass` can disable it. Button handler checks deduplication before recording.

### Join/Leave tracking: `on_voice_state_update` event
Bot listens to voice state changes. Only records events when a class is active and the member is in the tracked channel. Teacher's own join is excluded from student tracking.

### Report channel: configurable via env var
`REPORT_CHANNEL_ID` environment variable (or `.env` file). Report posted there on `!endclass`.

## Risks / Trade-offs

- **Single active session per guild** → teachers must `!endclass` before starting a new one. Mitigation: bot rejects `!start` if session already active, with helpful error.
- **In-memory state** → crash/restart loses session. Mitigation: acceptable for MVP; document limitation.
- **Role name coupling** → renaming Discord role breaks permission checks. Mitigation: make role name configurable via env var.
- **Button persistence across restarts** → old presence buttons remain after restart but won't work (View lost). Mitigation: bot edits message to disable button on startup if stale message ID stored (out of scope for MVP).

## Migration Plan

New project — no migration needed. Deploy steps:
1. Create Discord bot application, invite with required permissions
2. Set `DISCORD_TOKEN`, `REPORT_CHANNEL_ID`, `TEACHER_ROLE_NAME` in `.env`
3. Run bot: `python bot.py`

Rollback: stop bot process.
