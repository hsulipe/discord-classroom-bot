## 1. Enforce 32-char limit in `RegistrationModal`

- [x] 1.1 Change `max_length` from `80` to `32` in the `full_name` TextInput:
  ```python
  # before
  full_name = discord.ui.TextInput(
      label="Nome Completo",
      placeholder="ex.: João Silva",
      min_length=2,
      max_length=80,
  )
  # after
  full_name = discord.ui.TextInput(
      label="Nome Completo",
      placeholder="ex.: João Silva",
      min_length=2,
      max_length=32,
  )
  ```

## 2. Truncate nickname in `apply_registration`

- [x] 2.1 Add `nick = real_name[:32]` before `member.edit` and use `nick` in the call:
  ```python
  # before
  try:
      await member.edit(nick=real_name)
  except discord.Forbidden:
  # after
  nick = real_name[:32]
  try:
      await member.edit(nick=nick)
  except discord.Forbidden:
  ```

## 3. Testing

- [x] 3.1 Modal path: open the "Definir Meu Nome" modal → character counter shows /32 → typing beyond 32 chars is blocked by Discord UI
- [x] 3.2 `!register` with a name ≤ 32 chars → nickname applied as-is, no truncation
- [x] 3.3 `!register` with a name > 32 chars → nickname in Discord is truncated to 32 chars; full name appears in `names.json` and in the success message
- [x] 3.4 `!setname @member` with a name > 32 chars → same as 3.3 but for teacher command
