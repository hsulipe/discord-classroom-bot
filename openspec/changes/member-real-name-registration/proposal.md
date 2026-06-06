## Why

Discord usernames and server nicknames are unreliable identifiers for classroom attendance. A student whose real name is "John Silva" might appear in reports as "random123" or "xXgamer99Xx", making it impossible for teachers to match records to actual students. Attendance reports need to show real names to be usable for grading or administrative purposes.

## What Changes

- Add an `on_member_join` event that sends the new member a DM with a "Register Name" button
- Clicking the button opens a Discord modal (popup form) where the member types their full name
- Bot stores a persistent mapping of `member_id → real_name` in a JSON file so the data survives restarts
- `build_report()` looks up the stored real name for each member ID, falling back to `display_name` if not registered
- Add a `!register` command so existing members (who joined before this feature) can register their name at any time
- Add a `!setname @member RealName` command for teachers to manually set a name (edge case: student cannot interact with DM)

## Capabilities

### New Capabilities

- `member-registration`: On-join DM flow with modal form to capture real name; stored persistently per guild
- `manual-name-override`: Teacher command to set or correct a member's registered name

### Modified Capabilities

- `attendance-report`: Uses registered real name when available instead of Discord display name

## Impact

- Modifies `build_report()` in `bot.py` to resolve names from the registry
- Adds `on_member_join` event handler in `bot.py`
- Adds `!register` and `!setname` prefix commands in `bot.py`
- Adds a new `discord.ui.Modal` subclass and a `discord.ui.View` for the registration button
- Requires a JSON file (e.g., `names.json`) for persistence — no external DB needed
- Requires bot permission to send DMs to new members (DMs from server bots are allowed by default unless the user has DMs disabled)
