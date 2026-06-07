## Context

Single-file bot (`bot.py`, Python + discord.py 2.x). All user-visible strings are hardcoded inline. No i18n library is in use. The change is translate-only: every English string shown to a Discord user becomes Portuguese. Logger calls, runtime exceptions, and internal comments stay in English.

## Goals / Non-Goals

**Goals:**
- Every string a Discord user can read (channel messages, ephemeral replies, modal/button labels, report text) is in Brazilian Portuguese
- Developer-facing output (logging, exception messages) stays in English

**Non-Goals:**
- Multi-language support or runtime language switching
- Extracting strings to a separate constants or locale file (single-file codebase; inline is fine)
- Translating the `README.md` or any documentation

## Decisions

### Inline replacement, no i18n library

The bot is a single Python file with no existing abstraction layer. Introducing `gettext` or a locale module would add complexity with no benefit for a monolingual deployment. Direct string replacement keeps the diff minimal and readable.

### Brazilian Portuguese as the target

The classroom context implies Brazilian Portuguese. Formal register (`você`, not `tu`) is used throughout to match a classroom setting.

### Logger and internal errors remain in English

`logger.warning/error` calls and `RuntimeError` messages in `__main__` are developer-facing. Translating them would make debugging harder with no user-visible benefit.

### `apply_registration` issue strings are translated

Although these strings are assembled inside `apply_registration` and rendered by the caller, they are shown directly to the user in ephemeral followup messages. They include Discord UI references (e.g., "Server Settings → Roles") — translate these to Portuguese too, keeping the UI path names recognizable (Discord's own UI is localized in Brazil, so the canonical path names are used).

## String Translation Map

### `on_member_join` — welcome channel public message
```
EN: "Welcome {member.mention}! Check your private thread to complete registration."
PT: "Bem-vindo(a) {member.mention}! Verifique seu tópico privado para concluir o cadastro."
```

### `on_member_join` — private thread prompt
```
EN: "Hi {member.mention}! Please register your real name so the teacher can identify you in attendance reports."
PT: "Olá {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença."
```

### `on_member_join` — DM fallback
```
EN: "Welcome {member.mention}! Please register your real name so the teacher can identify you in attendance reports."
PT: "Bem-vindo(a) {member.mention}! Por favor, cadastre seu nome real para que o professor possa identificá-lo(a) nos relatórios de presença."
```

### `RegistrationModal` — UI elements
```
title:
  EN: "Register Your Name"
  PT: "Cadastre seu Nome"

full_name label:
  EN: "Full Name"
  PT: "Nome Completo"

full_name placeholder:
  EN: "e.g. John Silva"
  PT: "ex.: João Silva"
```

### `RegistrationModal.on_submit` — confirmation
```
EN: "Name registered as **{real_name}**. It will appear in attendance reports."
PT: "Nome cadastrado como **{real_name}**. Ele aparecerá nos relatórios de presença."
```

### `RegistrationModal.on_submit` — partial failure followup
```
EN: "⚠️ Name saved, but the following could not be applied:\n• ..."
PT: "⚠️ Nome salvo, mas os itens a seguir não puderam ser aplicados:\n• ..."
```

### `RegistrationModal.on_submit` — welcome message edit (legacy path)
```
EN: "✅ **{real_name}** has registered."
PT: "✅ **{real_name}** realizou o cadastro."
```

### `RegistrationView` — button label
```
EN: "Set My Name"
PT: "Definir Meu Nome"
```

### `apply_registration` — issue strings
```
nickname issue:
  EN: "nickname — bot needs **Manage Nicknames** permission and its role must be above yours in Server Settings → Roles"
  PT: "apelido — o bot precisa da permissão **Gerenciar Apelidos** e seu cargo deve estar acima do seu em Configurações do Servidor → Cargos"

role assign issue:
  EN: "role **{MEMBER_ROLE_NAME}** — bot role must be above **{MEMBER_ROLE_NAME}** in Server Settings → Roles"
  PT: "cargo **{MEMBER_ROLE_NAME}** — o cargo do bot deve estar acima de **{MEMBER_ROLE_NAME}** em Configurações do Servidor → Cargos"

role not found issue:
  EN: "role **{MEMBER_ROLE_NAME}** — role not found, check `MEMBER_ROLE_NAME` in `.env`"
  PT: "cargo **{MEMBER_ROLE_NAME}** — cargo não encontrado, verifique `MEMBER_ROLE_NAME` no `.env`"
```

### `close_presence` — edit text
```
EN: "Presence check closed."
PT: "Verificação de presença encerrada."
```

### `PresenceView` — button label
```
EN: "Sign Presence"
PT: "Assinar Presença"
```

### `PresenceView.sign_presence` — responses
```
no open check:
  EN: "No open presence check."
  PT: "Nenhuma verificação de presença aberta."

already signed:
  EN: "You already signed presence."
  PT: "Você já assinou a presença."

success:
  EN: "Presence signed!"
  PT: "Presença assinada!"
```

### `cmd_register` — responses
```
usage error:
  EN: "Usage: `!register Your Full Name`"
  PT: "Uso: `!register Seu Nome Completo`"

partial failure:
  EN: "Name saved as **{real_name}**, but the following could not be applied:\n• ..."
  PT: "Nome salvo como **{real_name}**, mas os itens a seguir não puderam ser aplicados:\n• ..."

success:
  EN: "Registered as **{real_name}**. Nickname and role updated."
  PT: "Cadastrado como **{real_name}**. Apelido e cargo atualizados."
```

### `cmd_setname` — responses
```
permission denied:
  EN: "Permission denied: Teacher role required."
  PT: "Permissão negada: cargo de Professor necessário."

usage error:
  EN: "Usage: `!setname @member Their Full Name`"
  PT: "Uso: `!setname @membro Nome Completo`"

partial failure:
  EN: "Name saved as **{real_name}** for {member.mention}, but the following could not be applied:\n• ..."
  PT: "Nome salvo como **{real_name}** para {member.mention}, mas os itens a seguir não puderam ser aplicados:\n• ..."

success:
  EN: "Set {member.mention}'s name to **{real_name}**, nickname and role updated."
  PT: "Nome de {member.mention} definido como **{real_name}**, apelido e cargo atualizados."

error handler — member not found:
  EN: "Member `{error.argument}` not found. Use a proper Discord mention: type `!setname ` then **@** and click the member's name from the autocomplete list."
  PT: "Membro `{error.argument}` não encontrado. Use uma menção válida do Discord: digite `!setname ` seguido de **@** e clique no nome do membro na lista de autocompletar."

error handler — missing argument:
  EN: "Usage: `!setname @member Their Full Name`"
  PT: "Uso: `!setname @membro Nome Completo`"

DM to member (set by teacher):
  EN: "Your attendance name has been set to **{real_name}** by the teacher."
  PT: "Seu nome para presença foi definido como **{real_name}** pelo professor."
```

### `cmd_start` — responses
```
permission denied:
  EN: "Permission denied: Teacher role required."
  PT: "Permissão negada: cargo de Professor necessário."

already in progress:
  EN: "A class is already in progress. Use `!endclass` first."
  PT: "Já há uma aula em andamento. Use `!endclass` primeiro."

not in voice:
  EN: "You must be in a voice channel to start a class."
  PT: "Você precisa estar em um canal de voz para iniciar uma aula."

success (no class name):
  EN: "Class started in **{channel.name}**. Tracking attendance ({count} student(s) already present)."
  PT: "Aula iniciada em **{channel.name}**. Monitorando presença ({count} aluno(s) já presente(s))."

success (with class name):
  EN: 'Class "{new_session.class_name}" started in **{channel.name}**. Tracking attendance ({count} student(s) already present).'
  PT: 'Aula "{new_session.class_name}" iniciada em **{channel.name}**. Monitorando presença ({count} aluno(s) já presente(s)).'
```

### `cmd_endclass` — responses
```
permission denied:
  EN: "Permission denied: Teacher role required."
  PT: "Permissão negada: cargo de Professor necessário."

no class in progress:
  EN: "No class is in progress."
  PT: "Nenhuma aula em andamento."

success (report in channel):
  EN: "Class ended. Report posted to {report_channel.mention}."
  PT: "Aula encerrada. Relatório enviado para {report_channel.mention}."

misconfigured report channel:
  EN: "Class ended, but the report channel is misconfigured (REPORT_CHANNEL_ID=...). Report:\n..."
  PT: "Aula encerrada, mas o canal de relatório está mal configurado (REPORT_CHANNEL_ID=...). Relatório:\n..."
```

### `cmd_presence` — responses
```
permission denied:
  EN: "Permission denied: Teacher role required."
  PT: "Permissão negada: cargo de Professor necessário."

no active session:
  EN: "No active class session."
  PT: "Nenhuma aula ativa no momento."

presence open:
  EN: "Presence check open! Click the button or type `!present`."
  PT: "Verificação de presença aberta! Clique no botão ou digite `!present`."
```

### `cmd_present` — responses
```
no active session:
  EN: "No active class session."
  PT: "Nenhuma aula ativa no momento."

no open check:
  EN: "No open presence check right now."
  PT: "Nenhuma verificação de presença aberta no momento."

already signed:
  EN: "You already signed presence."
  PT: "Você já assinou a presença."

success:
  EN: "{ctx.author.display_name} signed presence. ✅"
  PT: "{ctx.author.display_name} assinou a presença. ✅"
```

### `build_report` — report text
```
header:
  EN: "**Attendance Report**"
  PT: "**Relatório de Presença**"

class label:
  EN: "Class  :"
  PT: "Turma  :"

start label:
  EN: "Start  :"
  PT: "Início :"

end label:
  EN: "End    :"
  PT: "Fim    :"

duration label:
  EN: "Duration:"
  PT: "Duração :"

total students label:
  EN: "Total students:"
  PT: "Total de alunos:"

no students attended:
  EN: "No students attended."
  PT: "Nenhum aluno participou."

table header — Name column:
  EN: "Name"
  PT: "Nome"

table header — Time in session column:
  EN: "Time in session"
  PT: "Tempo na aula"

table header — Presence column (inline):
  EN: "Presence"
  PT: "Presença"

status — confirmed:
  EN: "Confirmed present"
  PT: "Presença confirmada"

status — joined only:
  EN: "Joined only"
  PT: "Apenas entrou"
```

## Risks / Trade-offs

- **Column alignment in the report**: The Portuguese strings ("Presença confirmada", "Apenas entrou") are longer than their English equivalents. The `<24` and `<18` padding widths may need review to keep the ```` ``` ```` table readable. Adjust the padding constants if the Portuguese strings overflow.
- **Gender-neutral phrasing**: Forms like "Bem-vindo(a)" and "identificá-lo(a)" cover both genders without the complexity of dynamic gender agreement. Acceptable for a classroom bot.
- **"Teacher" role name stays English**: `TEACHER_ROLE_NAME` defaults to `"Teacher"` and is compared against actual Discord role names in the server. The bot's permission-check messages say "cargo de Professor" in Portuguese, but the `.env` variable still controls the actual role name matched. No behavior change.
