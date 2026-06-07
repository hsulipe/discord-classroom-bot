## Why

The bot is used in a Portuguese-speaking classroom. All user-visible messages are currently in English, creating a friction point for students and teachers who interact with the bot daily. Translating to Portuguese makes the experience consistent with the classroom's language, reduces confusion, and removes the need for users to interpret English instructions.

## What Changes

- All user-facing strings in `bot.py` are translated to Brazilian Portuguese
- UI labels (button text, modal title, text input label and placeholder) are translated
- Attendance report headers and presence status values are translated
- Internal developer messages (logger calls, runtime errors) remain in English

## Capabilities

### New Capabilities

_None_ — this is a localization-only change with no behavioral differences.

### Modified Capabilities

- `member-registration`: Welcome message, private-thread prompt, DM fallback, modal title/label, button label, registration confirmation, and error messages are all in Portuguese
- `presence-check`: Presence button label, open/close announcements, signed confirmation messages are in Portuguese
- `attendance-report`: Report headers, column names, and per-member status values ("Confirmed present" / "Joined only") are in Portuguese
- `teacher-commands`: All command error messages, usage hints, and success confirmations are in Portuguese

## Impact

- Single file change: `bot.py`
- No behavioral changes — only string content differs
- No new dependencies
- Fully backward-compatible: all commands, events, and flows work identically
