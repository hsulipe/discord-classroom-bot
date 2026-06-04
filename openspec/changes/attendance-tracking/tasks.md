## 1. Project Setup

- [x] 1.1 Create `bot.py` entry point, `requirements.txt` with `discord.py>=2.0`, and `.env.example` with `DISCORD_TOKEN`, `REPORT_CHANNEL_ID`, `TEACHER_ROLE_NAME`
- [x] 1.2 Initialize `commands.Bot` with prefix `!` and intents for `guilds`, `voice_states`, `message_content`, `members`
- [x] 1.3 Add `python-dotenv` loading for environment variables on startup

## 2. Session State

- [x] 2.1 Create `SessionState` dataclass (or dict schema) holding: `active`, `voice_channel_id`, `start_time`, `join_leave_log`, `presence_checks`, `active_presence_message`
- [x] 2.2 Create a per-guild session registry (dict keyed by guild ID) accessible to all command handlers

## 3. Class Lifecycle Commands

- [x] 3.1 Implement `!start` — validate Teacher role, validate author in voice channel, reject if session active, create session, confirm
- [x] 3.2 Implement `!endclass` — validate Teacher role, reject if no active session, trigger presence close + report generation, clear session state
- [x] 3.3 Register `on_voice_state_update` event handler — only record events when session active and channel matches tracked channel, skip teacher

## 4. Presence Check Commands

- [x] 4.1 Implement `!presence` — validate Teacher role, validate active session, create `discord.ui.View` with "Sign Presence" button, post message, store message reference in session
- [x] 4.2 Implement button interaction handler — check no duplicate, record student ID in current presence check signatories, reply ephemeral confirmation
- [x] 4.3 Implement `!present` command — same dedup logic as button, record signature, confirm in channel
- [x] 4.4 Implement `close_presence()` helper — disables button (edits message), marks presence check closed; called by `!endclass` and optionally by new `!presence`

## 5. Attendance Report

- [x] 5.1 Implement `build_report(session)` — compute per-member time in session from join/leave log (treat missing leave as session end time), flag presence signatories
- [x] 5.2 Implement `post_report(bot, session, guild)` — fetch report channel by `REPORT_CHANNEL_ID`, format report as embedded message or code block, post it
- [x] 5.3 Handle misconfigured report channel — log error and reply to teacher in command channel

## 6. Error Handling & Edge Cases

- [x] 6.1 Handle member already in voice channel at `!start` time — add them to session log as an initial join event
- [x] 6.2 Ensure `!endclass` with no presence check open skips close step without error
- [x] 6.3 Add guard so non-Teacher users get a clear error on `!start`, `!endclass`, `!presence`

## 7. Testing

- [ ] 7.1 Manual test: full happy-path flow (start → join → presence → present → endclass → report posted)
- [ ] 7.2 Manual test: duplicate `!present` rejected
- [ ] 7.3 Manual test: `!start` while session active rejected
- [ ] 7.4 Manual test: `!endclass` disables presence button if open
<!-- Manual tests require a live Discord server with bot token configured in .env -->
