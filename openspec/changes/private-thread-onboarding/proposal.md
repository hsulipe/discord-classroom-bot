## Why

The welcome message currently posts in the welcome channel with a "Set My Name" button visible to all server members. Any member can click it — opening the registration modal under their own identity. While the modal saves by `interaction.user.id` (so clicking doesn't corrupt another member's name), the button clutters the channel and creates confusion: existing members see a button that appears directed at them, and the new member's onboarding flow is visually exposed to the whole server.

The fix: keep a brief public announcement in the welcome channel (so the community sees new members arriving), but move the registration form into a private thread visible only to the new member and the bot.

## What Changes

- `on_member_join` posts a short public announcement in the welcome channel (no button)
- Bot immediately creates a private thread in the welcome channel, adds only the new member
- Registration message with `[Set My Name]` button is posted inside the private thread
- After the member submits their name, the bot archives the thread automatically
- `RegistrationView` and `RegistrationModal` receive an optional `thread` reference for archival
- DM fallback (when no welcome channel is configured) is unchanged

## Capabilities

### New Capabilities

_None_ — this is an enhancement to an existing capability.

### Modified Capabilities

- `member-registration`: On-join flow moves from a public welcome-channel message to a private thread. The thread is visible only to the new member; it is archived automatically after registration.

## Impact

- Single file change: `bot.py`
- Bot requires two additional Discord permissions: `Create Private Threads`, `Manage Threads`
- `welcome_messages` dict and post-registration message-edit flow become unused for the thread path (thread archival replaces it); DM fallback path is unchanged
- Fully backward-compatible: servers without `WELCOME_CHANNEL_ID` continue to use DM fallback
