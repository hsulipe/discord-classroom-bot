## 1. Translate `apply_registration` issue strings

- [x] 1.1 Replace nickname issue string:
  ```python
  # before
  issues.append("nickname — bot needs **Manage Nicknames** permission and its role must be above yours in Server Settings → Roles")
  # after
  issues.append("apelido — o bot precisa da permissão **Gerenciar Apelidos** e seu cargo deve estar acima do seu em Configurações do Servidor → Cargos")
  ```
- [x] 1.2 Replace role-assign issue string:
  ```python
  # before
  issues.append(f"role **{MEMBER_ROLE_NAME}** — bot role must be above **{MEMBER_ROLE_NAME}** in Server Settings → Roles")
  # after
  issues.append(f"cargo **{MEMBER_ROLE_NAME}** — o cargo do bot deve estar acima de **{MEMBER_ROLE_NAME}** em Configurações do Servidor → Cargos")
  ```
- [x] 1.3 Replace role-not-found issue string:
  ```python
  # before
  issues.append(f"role **{MEMBER_ROLE_NAME}** — role not found, check `MEMBER_ROLE_NAME` in `.env`")
  # after
  issues.append(f"cargo **{MEMBER_ROLE_NAME}** — cargo não encontrado, verifique `MEMBER_ROLE_NAME` no `.env`")
  ```

## 2. Translate `close_presence`

- [x] 2.1 Replace closed message:
  ```python
  # before
  await pc.message.edit(content="Presence check closed.", view=pc.view)
  # after
  await pc.message.edit(content="Verificação de presença encerrada.", view=pc.view)
  ```

## 3. Translate `on_member_join`

- [x] 3.1 Replace public welcome channel announcement:
  ```python
  # before
  await channel.send(f"Welcome {member.mention}! Check your private thread to complete registration.")
  # after
  await channel.send(f"Bem-vindo(a) {member.mention}! Verifique seu tópico privado para concluir o cadastro.")
  ```
- [x] 3.2 Replace private thread prompt:
  ```python
  # before
  await thread.send(
      f"Hi {member.mention}! Please register your real name so the teacher can identify you in attendance reports.",
      view=RegistrationView(thread=thread),
  )
  # after
  await thread.send(
      f"Olá {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença.",
      view=RegistrationView(thread=thread),
  )
  ```
- [x] 3.3 Replace DM fallback message:
  ```python
  # before
  await member.send(
      f"Welcome {member.mention}! Please register your real name so the teacher can identify you in attendance reports.",
      view=RegistrationView(),
  )
  # after
  await member.send(
      f"Bem-vindo(a) {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença.",
      view=RegistrationView(),
  )
  ```

## 4. Translate `RegistrationModal`

- [x] 4.1 Change modal title:
  ```python
  # before
  class RegistrationModal(discord.ui.Modal, title="Register Your Name"):
  # after
  class RegistrationModal(discord.ui.Modal, title="Cadastre seu Nome"):
  ```
- [x] 4.2 Change `full_name` TextInput label and placeholder:
  ```python
  # before
  full_name = discord.ui.TextInput(
      label="Full Name",
      placeholder="e.g. John Silva",
      ...
  )
  # after
  full_name = discord.ui.TextInput(
      label="Nome Completo",
      placeholder="ex.: João Silva",
      ...
  )
  ```
- [x] 4.3 Replace registration confirmation message:
  ```python
  # before
  await interaction.response.send_message(
      f"Name registered as **{real_name}**. It will appear in attendance reports.",
      ephemeral=True,
  )
  # after
  await interaction.response.send_message(
      f"Nome cadastrado como **{real_name}**. Ele aparecerá nos relatórios de presença.",
      ephemeral=True,
  )
  ```
- [x] 4.4 Replace partial-failure followup message:
  ```python
  # before
  await interaction.followup.send(
      f"⚠️ Name saved, but the following could not be applied:\n"
      + "\n".join(f"• {i}" for i in issues),
      ephemeral=True,
  )
  # after
  await interaction.followup.send(
      f"⚠️ Nome salvo, mas os itens a seguir não puderam ser aplicados:\n"
      + "\n".join(f"• {i}" for i in issues),
      ephemeral=True,
  )
  ```
- [x] 4.5 Replace legacy welcome message edit content:
  ```python
  # before
  await msg.edit(content=f"✅ **{real_name}** has registered.", view=None)
  # after
  await msg.edit(content=f"✅ **{real_name}** realizou o cadastro.", view=None)
  ```

## 5. Translate `RegistrationView`

- [x] 5.1 Change button label:
  ```python
  # before
  @discord.ui.button(label="Set My Name", style=discord.ButtonStyle.primary)
  # after
  @discord.ui.button(label="Definir Meu Nome", style=discord.ButtonStyle.primary)
  ```

## 6. Translate `PresenceView`

- [x] 6.1 Change button label:
  ```python
  # before
  @discord.ui.button(label="Sign Presence", style=discord.ButtonStyle.green, emoji="✅")
  # after
  @discord.ui.button(label="Assinar Presença", style=discord.ButtonStyle.green, emoji="✅")
  ```
- [x] 6.2 Replace "no open presence check" ephemeral:
  ```python
  # before
  await interaction.response.send_message("No open presence check.", ephemeral=True)
  # after
  await interaction.response.send_message("Nenhuma verificação de presença aberta.", ephemeral=True)
  ```
- [x] 6.3 Replace "already signed" ephemeral in `PresenceView`:
  ```python
  # before
  await interaction.response.send_message("You already signed presence.", ephemeral=True)
  # after
  await interaction.response.send_message("Você já assinou a presença.", ephemeral=True)
  ```
- [x] 6.4 Replace "Presence signed!" ephemeral:
  ```python
  # before
  await interaction.response.send_message("Presence signed!", ephemeral=True)
  # after
  await interaction.response.send_message("Presença assinada!", ephemeral=True)
  ```

## 7. Translate `cmd_register`

- [x] 7.1 Replace usage error:
  ```python
  # before
  await ctx.send("Usage: `!register Your Full Name`")
  # after
  await ctx.send("Uso: `!register Seu Nome Completo`")
  ```
- [x] 7.2 Replace partial-failure message:
  ```python
  # before
  await ctx.send(
      f"Name saved as **{real_name}**, but the following could not be applied:\n"
      + "\n".join(f"• {i}" for i in issues)
  )
  # after
  await ctx.send(
      f"Nome salvo como **{real_name}**, mas os itens a seguir não puderam ser aplicados:\n"
      + "\n".join(f"• {i}" for i in issues)
  )
  ```
- [x] 7.3 Replace success message:
  ```python
  # before
  await ctx.send(f"Registered as **{real_name}**. Nickname and role updated.")
  # after
  await ctx.send(f"Cadastrado como **{real_name}**. Apelido e cargo atualizados.")
  ```

## 8. Translate `cmd_setname`

- [x] 8.1 Replace permission denied:
  ```python
  # before
  await ctx.send("Permission denied: Teacher role required.")
  # after
  await ctx.send("Permissão negada: cargo de Professor necessário.")
  ```
- [x] 8.2 Replace usage error:
  ```python
  # before
  await ctx.send("Usage: `!setname @member Their Full Name`")
  # after
  await ctx.send("Uso: `!setname @membro Nome Completo`")
  ```
- [x] 8.3 Replace partial-failure message:
  ```python
  # before
  await ctx.send(
      f"Name saved as **{real_name}** for {member.mention}, but the following could not be applied:\n"
      + "\n".join(f"• {i}" for i in issues)
  )
  # after
  await ctx.send(
      f"Nome salvo como **{real_name}** para {member.mention}, mas os itens a seguir não puderam ser aplicados:\n"
      + "\n".join(f"• {i}" for i in issues)
  )
  ```
- [x] 8.4 Replace success message:
  ```python
  # before
  await ctx.send(f"Set {member.mention}'s name to **{real_name}**, nickname and role updated.")
  # after
  await ctx.send(f"Nome de {member.mention} definido como **{real_name}**, apelido e cargo atualizados.")
  ```
- [x] 8.5 Translate error handler — member not found:
  ```python
  # before
  await ctx.send(
      f"Member `{error.argument}` not found. "
      "Use a proper Discord mention: type `!setname ` then **@** and click the member's name from the autocomplete list."
  )
  # after
  await ctx.send(
      f"Membro `{error.argument}` não encontrado. "
      "Use uma menção válida do Discord: digite `!setname ` seguido de **@** e clique no nome do membro na lista de autocompletar."
  )
  ```
- [x] 8.6 Translate error handler — missing argument:
  ```python
  # before
  await ctx.send("Usage: `!setname @member Their Full Name`")
  # after
  await ctx.send("Uso: `!setname @membro Nome Completo`")
  ```
- [x] 8.7 Translate DM to member (sent by teacher):
  ```python
  # before
  await member.send(
      f"Your attendance name has been set to **{real_name}** by the teacher."
  )
  # after
  await member.send(
      f"Seu nome para presença foi definido como **{real_name}** pelo professor."
  )
  ```

## 9. Translate `cmd_start`

- [x] 9.1 Replace permission denied (shares string with other commands — update each occurrence):
  ```python
  # before
  await ctx.send("Permission denied: Teacher role required.")
  # after
  await ctx.send("Permissão negada: cargo de Professor necessário.")
  ```
- [x] 9.2 Replace "already in progress" error:
  ```python
  # before
  await ctx.send("A class is already in progress. Use `!endclass` first.")
  # after
  await ctx.send("Já há uma aula em andamento. Use `!endclass` primeiro.")
  ```
- [x] 9.3 Replace "must be in voice channel" error:
  ```python
  # before
  await ctx.send("You must be in a voice channel to start a class.")
  # after
  await ctx.send("Você precisa estar em um canal de voz para iniciar uma aula.")
  ```
- [x] 9.4 Replace success message (update `label` variable construction and the `ctx.send` call):
  ```python
  # before
  label = f'Class "{new_session.class_name}" started' if new_session.class_name else "Class started"
  await ctx.send(
      f"{label} in **{channel.name}**. "
      f"Tracking attendance ({count} student(s) already present)."
  )
  # after
  label = f'Aula "{new_session.class_name}" iniciada' if new_session.class_name else "Aula iniciada"
  await ctx.send(
      f"{label} em **{channel.name}**. "
      f"Monitorando presença ({count} aluno(s) já presente(s))."
  )
  ```

## 10. Translate `cmd_endclass`

- [x] 10.1 Replace permission denied.
- [x] 10.2 Replace "no class in progress":
  ```python
  # before
  await ctx.send("No class is in progress.")
  # after
  await ctx.send("Nenhuma aula em andamento.")
  ```
- [x] 10.3 Replace success message:
  ```python
  # before
  await ctx.send(f"Class ended. Report posted to {report_channel.mention}.")
  # after
  await ctx.send(f"Aula encerrada. Relatório enviado para {report_channel.mention}.")
  ```
- [x] 10.4 Replace misconfigured-channel error:
  ```python
  # before
  await ctx.send(
      "Class ended, but the report channel is misconfigured "
      f"(REPORT_CHANNEL_ID={REPORT_CHANNEL_ID!r}). Report:\n{report}"
  )
  # after
  await ctx.send(
      "Aula encerrada, mas o canal de relatório está mal configurado "
      f"(REPORT_CHANNEL_ID={REPORT_CHANNEL_ID!r}). Relatório:\n{report}"
  )
  ```

## 11. Translate `cmd_presence`

- [x] 11.1 Replace permission denied.
- [x] 11.2 Replace "no active class session":
  ```python
  # before
  await ctx.send("No active class session.")
  # after
  await ctx.send("Nenhuma aula ativa no momento.")
  ```
- [x] 11.3 Replace presence open message:
  ```python
  # before
  msg = await ctx.send(
      "Presence check open! Click the button or type `!present`.",
      view=view,
  )
  # after
  msg = await ctx.send(
      "Verificação de presença aberta! Clique no botão ou digite `!present`.",
      view=view,
  )
  ```

## 12. Translate `cmd_present`

- [x] 12.1 Replace "no active class session".
- [x] 12.2 Replace "no open presence check right now":
  ```python
  # before
  await ctx.send("No open presence check right now.")
  # after
  await ctx.send("Nenhuma verificação de presença aberta no momento.")
  ```
- [x] 12.3 Replace "already signed presence" in `cmd_present`:
  ```python
  # before
  await ctx.send("You already signed presence.")
  # after
  await ctx.send("Você já assinou a presença.")
  ```
- [x] 12.4 Replace success message:
  ```python
  # before
  await ctx.send(f"{ctx.author.display_name} signed presence. ✅")
  # after
  await ctx.send(f"{ctx.author.display_name} assinou a presença. ✅")
  ```

## 13. Translate `build_report`

- [x] 13.1 Replace report header and field labels:
  ```python
  # before
  lines = ["**Attendance Report**"]
  if session.class_name:
      lines.append(f"Class  : {session.class_name}")
  lines += [
      f"Start  : {session.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
      f"End    : {end.strftime('%Y-%m-%d %H:%M:%S UTC')}",
      f"Duration: {h}h {m}m {s}s",
      f"Total students: {len(member_ids)}",
      "",
  ]
  # after
  lines = ["**Relatório de Presença**"]
  if session.class_name:
      lines.append(f"Turma  : {session.class_name}")
  lines += [
      f"Início : {session.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
      f"Fim    : {end.strftime('%Y-%m-%d %H:%M:%S UTC')}",
      f"Duração: {h}h {m}m {s}s",
      f"Total de alunos: {len(member_ids)}",
      "",
  ]
  ```
- [x] 13.2 Replace "No students attended.":
  ```python
  # before
  lines.append("No students attended.")
  # after
  lines.append("Nenhum aluno participou.")
  ```
- [x] 13.3 Replace table header line:
  ```python
  # before
  lines.append(f"{'Name':<24} {'Time in session':<18} Presence")
  # after
  lines.append(f"{'Nome':<24} {'Tempo na aula':<18} Presença")
  ```
- [x] 13.4 Replace per-member status values:
  ```python
  # before
  status = "Confirmed present" if mid in all_signatories else "Joined only"
  # after
  status = "Presença confirmada" if mid in all_signatories else "Apenas entrou"
  ```

## 14. Testing

- [x] 14.1 New member joins with `WELCOME_CHANNEL_ID` set → public welcome message and private thread prompt are in Portuguese
- [x] 14.2 New member joins without `WELCOME_CHANNEL_ID` → DM message is in Portuguese
- [x] 14.3 Member clicks "Definir Meu Nome" button → modal title and label are in Portuguese → submission shows Portuguese confirmation
- [x] 14.4 `!register Nome Completo` → success message in Portuguese; error message when no name given is in Portuguese
- [x] 14.5 `!setname @membro Nome` (teacher) → success message in Portuguese; member DM in Portuguese
- [x] 14.6 `!start` → permission error in Portuguese; "not in voice" error in Portuguese; success message in Portuguese
- [x] 14.7 `!endclass` → report header, labels, table, and status values are in Portuguese
- [x] 14.8 `!presence` → button label and open announcement are in Portuguese; clicking button shows Portuguese ephemeral
- [x] 14.9 `!present` → all response messages are in Portuguese
