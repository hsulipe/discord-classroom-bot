## 1. Name Registry Storage

- [x] 1.1 Add `NAMES_FILE = "names.json"` constant and `names: dict[str, str] = {}` module-level dict in `bot.py`
- [x] 1.2 Add `load_names()` function — reads `names.json` if it exists, populates `names` dict; called once at the bottom of `bot.py` before `bot.run()`
- [x] 1.3 Add `save_names()` function — writes `names` dict to `names.json` atomically (write to `.tmp` then `os.replace`)

## 2. Registration Modal and View

- [x] 2.1 Implement `RegistrationModal(discord.ui.Modal)` — single `discord.ui.TextInput` labeled "Full Name", `on_submit` saves `str(interaction.user.id)` → stripped input to `names`, calls `save_names()`, sends ephemeral confirmation
- [x] 2.2 Implement `RegistrationView(discord.ui.View)` — single button "Set My Name" (style=primary), button callback calls `await interaction.response.send_modal(RegistrationModal())`

## 3. On-Join DM Flow

- [x] 3.1 Add `on_member_join(member)` event handler — sends DM to `member` with a welcome message and a `RegistrationView`; wraps the DM send in `try/except discord.Forbidden` and logs a warning on failure (DMs disabled)

## 4. Self-Service `!register` Command

- [x] 4.1 Implement `!register` command — accepts remaining text as the full name (`ctx.message.content` after command prefix), strips whitespace, rejects empty input with a usage hint, saves to `names`, calls `save_names()`, confirms with a message showing the saved name

## 5. Teacher `!setname` Command

- [x] 5.1 Implement `!setname` command — requires Teacher role; expects one `discord.Member` mention and a name string as arguments; saves to `names`, calls `save_names()`, confirms to teacher; sends a DM to the affected member notifying them of the change

## 6. Update Report Name Resolution

- [x] 6.1 In `build_report()`, replace `member.display_name if member else f"<id:{mid}>"` with a helper `resolve_name(mid, guild)` that checks `names.get(str(mid))` first, then `guild.get_member(mid).display_name`, then `<id:{mid}>`

## 7. Testing

- [ ] 7.1 Manual test: new member joins → receives DM with button → clicks → modal appears → submits name → `names.json` updated → next report shows real name
- [ ] 7.2 Manual test: `!register First Last` updates name and confirms in channel
- [ ] 7.3 Manual test: teacher `!setname @member Full Name` saves correctly and DMs the member
- [ ] 7.4 Manual test: member with DMs disabled joins → no crash, warning logged, `!register` still works for them
- [ ] 7.5 Manual test: run `!endclass` after registration and verify report shows registered names, falls back to display name for unregistered members
