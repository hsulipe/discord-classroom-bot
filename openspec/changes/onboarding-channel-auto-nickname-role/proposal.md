## Why

The current on-join registration flow sends a DM to the new member. DMs are easy to miss, can be blocked by user settings, and leave no trace in the server itself. A visible welcome message in a dedicated channel creates a clearer onboarding experience while still keeping clutter away from other members (ephemeral — only the joining user sees it).

Once a student registers their name, two extra steps currently require manual teacher action: setting the server nickname and assigning the student role. Automating these removes friction and ensures new members are immediately identifiable by their real name throughout the server.

## What Changes

- Replace the on-join DM with an **ephemeral message in a configurable welcome channel**, visible only to the joining member, containing the "Set My Name" registration button
- After successful registration via the modal, **automatically set the member's server nickname** to the registered name
- After successful registration, **automatically assign a configurable member role** (e.g. "Student") to the member
- Add `WELCOME_CHANNEL_ID` and `MEMBER_ROLE_NAME` to the `.env` configuration

## Capabilities

### New Capabilities

- `welcome-channel-prompt`: On join, bot sends an ephemeral registration prompt in a designated welcome channel instead of a DM

### Modified Capabilities

- `member-registration`: After name submission, bot now also sets the server nickname and assigns the member role in addition to saving to `names.json`

## Impact

- Modifies `on_member_join` in `bot.py` — switches from `member.send()` to posting an ephemeral message in the welcome channel
- Modifies `RegistrationModal.on_submit()` in `bot.py` — adds `member.edit(nick=real_name)` and role assignment after saving the name
- Adds two new env vars: `WELCOME_CHANNEL_ID` and `MEMBER_ROLE_NAME`
- Requires bot permissions: **Manage Nicknames**, **Manage Roles**
- Bot role must be above the assigned member role in the server role hierarchy for role assignment to work
