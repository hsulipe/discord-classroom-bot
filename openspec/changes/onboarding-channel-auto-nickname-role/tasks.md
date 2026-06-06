## 1. New Environment Variables

- [x] 1.1 Add `WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID")` and `MEMBER_ROLE_NAME = os.getenv("MEMBER_ROLE_NAME")` constants in `bot.py` alongside the existing env vars
- [x] 1.2 Add `WELCOME_CHANNEL_ID` and `MEMBER_ROLE_NAME` entries to `.env.example` with descriptive comments

## 2. Post-Registration: Auto-Nickname and Auto-Role

- [x] 2.1 Add helper `async def apply_registration(member: discord.Member, real_name: str) -> None` — sets nickname via `member.edit(nick=real_name)` (catch `discord.Forbidden`, log warning); assigns role via `discord.utils.get(member.guild.roles, name=MEMBER_ROLE_NAME)` and `member.add_roles(role)` if role found (catch `discord.Forbidden`, log warning)
- [x] 2.2 Call `await apply_registration(interaction.user, real_name)` at the end of `RegistrationModal.on_submit()`, after `save_names()`
- [x] 2.3 Call `await apply_registration(ctx.author, real_name)` at the end of `cmd_register()`, after `save_names()`
- [x] 2.4 Call `await apply_registration(member, real_name)` at the end of `cmd_setname()`, after `save_names()`

## 3. Switch On-Join Prompt from DM to Welcome Channel

- [x] 3.1 Refactor `on_member_join` — if `WELCOME_CHANNEL_ID` is set, fetch the channel via `bot.get_channel(int(WELCOME_CHANNEL_ID))` and send the welcome message with `RegistrationView` there; otherwise fall back to the existing `member.send()` DM approach
- [x] 3.2 Store the welcome message object in a module-level dict `welcome_messages: dict[int, discord.Message] = {}` keyed by `member.id`, so `RegistrationModal.on_submit()` can edit it after registration
- [x] 3.3 In `RegistrationModal.on_submit()`, after calling `apply_registration()`, check `welcome_messages` for a pending message for this user; if found, edit it to `"✅ {real_name} has been registered."` and remove it from the dict

## 4. Update README

- [x] 4.1 Add `WELCOME_CHANNEL_ID` and `MEMBER_ROLE_NAME` to the env var table in the README
- [x] 4.2 Update the **Name Registration** section to describe the welcome channel flow (visible channel message with button) and mention that nickname and role are set automatically on submission
- [x] 4.3 Add required bot permissions (**Manage Nicknames**, **Manage Roles**) to the invite/permissions section

## 5. Testing

- [ ] 5.1 Manual test: new member joins → welcome message appears in welcome channel → clicks "Set My Name" → modal appears → submits name → nickname updated in server → member role assigned → welcome message edited to confirmation
- [ ] 5.2 Manual test: `WELCOME_CHANNEL_ID` not set → falls back to DM as before
- [ ] 5.3 Manual test: `MEMBER_ROLE_NAME` not set → registration completes without role assignment, no error
- [ ] 5.4 Manual test: bot role below member role in hierarchy → `Forbidden` caught, warning logged, registration still confirms to user
- [ ] 5.5 Manual test: `!register` and `!setname` also set nickname and role correctly
