## Context

Existing project: single-file `bot.py` (Python + discord.py 2.x), prefix commands, in-memory session state. No database — persistence is currently limited to a running process. The report generator in `build_report()` resolves display names via `guild.get_member(mid).display_name`.

## Goals / Non-Goals

**Goals:**
- Capture a member's real name once, on join, via a DM modal flow
- Persist the name registry across bot restarts
- Use the real name in all attendance reports
- Allow late registration via `!register` for members who joined before the feature
- Allow teachers to set/override a name via `!setname`

**Non-Goals:**
- Name validation (format, uniqueness) — trust the user's input
- Multi-guild name separation in the JSON file (names are per-member-ID globally; member IDs are globally unique in Discord)
- Re-asking members who dismiss the DM (one-shot on join; `!register` covers re-entry)
- Slash command migration (stays prefix-only, consistent with existing bot)

## Decisions

### Storage: JSON file (`names.json`)
A simple `{member_id_str: real_name}` JSON file loaded at startup and written on every registration. No external DB dependency. Tradeoff: not concurrent-safe if multiple bot instances run (not a concern here — single process).

### On-join flow: DM with View + Modal
`on_member_join` → bot sends DM with a `RegistrationView` containing a "Set My Name" button. Button callback opens a `RegistrationModal` (text input). On submit, name is saved and a confirmation DM is sent. If the user has DMs disabled, the join event is silently skipped — `!register` remains available as fallback.

### Why modal instead of a message-based prompt?
A modal (popup form) collects the name in one interaction without leaving a back-and-forth message thread in DMs. It is the idiomatic Discord UX for structured input. discord.py 2.x supports `discord.ui.Modal` natively.

### `!register` command: self-service name update
Any member can type `!register First Last` in any channel. Bot saves the name and confirms. This handles: (a) members who joined before the feature, (b) members who dismissed the DM, (c) name corrections.

### `!setname @member Name` command: teacher override
Restricted to Teacher role. Handles cases where a student cannot or will not register themselves (e.g., DMs disabled, technically challenged). The teacher enters the real name manually.

### `build_report()` name resolution order
1. Look up `str(member_id)` in the loaded `names` dict
2. Fall back to `guild.get_member(mid).display_name`
3. Fall back to `<id:{mid}>` if member left the guild

This means zero regressions — reports still work even if nobody registers.

### Names dict: module-level, loaded once
`names: dict[str, str] = {}` loaded from `names.json` at startup. Written back to disk synchronously on every update (dict is small; file I/O is negligible). No async locking needed for single-process bot.

## Risks / Trade-offs

- **DMs disabled**: If a student has server DMs disabled, the `on_member_join` DM will fail with `discord.Forbidden`. Bot catches this and logs a warning; no crash. Student can still use `!register`.
- **Name corrections require re-registration**: Users must re-run `!register` or ask a teacher for `!setname`. Acceptable — no complex edit flow needed.
- **JSON file deleted/corrupted**: Bot starts with empty registry; no crash, just falls back to display names. Teachers would need to re-collect names.

## Migration Plan

Existing members will not have entries in `names.json` on first deploy. Teachers should announce `!register YourFullName` in the server so students can self-register before the next class. No code migration needed — `build_report()` gracefully falls back to `display_name`.
