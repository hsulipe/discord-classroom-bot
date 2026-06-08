## Why

Discord enforces a hard 32-character limit on member nicknames. The bot currently passes the full registered name directly to `member.edit(nick=real_name)` without any length check. When the name exceeds 32 characters, Discord returns an HTTP 400 error that the bot does not handle, raising an unhandled `discord.HTTPException`. This silently breaks nickname assignment for students with longer names.

The modal `TextInput` also has `max_length=80`, so the UI itself offers no hint that nicknames are capped at 32 characters.

## What Changes

- `RegistrationModal.full_name` `max_length` changes from 80 → 32, making Discord's own character counter the in-modal warning
- `apply_registration` truncates `real_name` to 32 characters before calling `member.edit(nick=...)`, preventing the exception for all code paths (modal, `!register`, `!setname`)
- When truncation occurs (name entered via commands is > 32 chars), the applied nickname is still communicated clearly in the response

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `member-registration`: Modal now enforces 32-char max at input level; nickname application is guarded against overflow for all registration paths
- `teacher-commands`: `!setname` and `!register` will truncate the nickname portion to 32 chars while preserving the full name in `names.json` for attendance reports

## Impact

- Single file change: `bot.py`
- No new dependencies
- Names stored in `names.json` are unaffected (full name is kept for report accuracy); only the Discord nickname is truncated
- Fully backward-compatible
