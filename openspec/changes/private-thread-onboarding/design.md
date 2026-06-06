## Context

Existing project: single-file `bot.py` (Python + discord.py 2.x), prefix commands, in-memory session state. The current `on_member_join` handler posts a public message with a `RegistrationView` button in the welcome channel. `RegistrationView` opens `RegistrationModal`, which saves `interaction.user.id → real_name` and edits the original welcome message to show a ✅ confirmation.

## Goals / Non-Goals

**Goals:**
- New member's registration form is private (only they and the bot can see it)
- Welcome channel retains a brief public announcement per new member
- Thread is automatically cleaned up (archived) after registration
- DM fallback path when no welcome channel is set remains unchanged

**Non-Goals:**
- Migrating to slash commands (stays prefix-only, consistent with existing bot)
- Thread naming conventions or aesthetics beyond a sensible default
- Handling members who never register (thread times out via Discord's own inactivity archival)

## Decisions

### Private thread instead of ephemeral message

`on_member_join` is a bot-initiated event with no Discord interaction to respond to. Ephemeral messages require an interaction response — they cannot be sent proactively. A private thread (`ChannelType.private_thread`) is the only channel-native mechanism that restricts visibility to specific members without requiring an interaction trigger.

### Thread per new member

One thread per join event. The thread is named `"Welcome {member.display_name}"` for easy identification by moderators (who can see private threads via Manage Threads permission). Thread is created with `invitable=False` so only the bot can add members.

### Thread reference passed through View → Modal

`RegistrationView` accepts an optional `thread: discord.Thread` parameter. It passes this to `RegistrationModal` when opening it. `RegistrationModal.on_submit` archives the thread after saving the name. Both classes default to `None` so the DM fallback continues to work with no thread argument.

```
on_member_join
  └─► channel.create_thread(private_thread, invitable=False)
  └─► thread.add_user(member)
  └─► thread.send(registration_text, view=RegistrationView(thread=thread))

RegistrationView.set_name (button click)
  └─► interaction.response.send_modal(RegistrationModal(thread=self.thread))

RegistrationModal.on_submit
  └─► save name
  └─► apply_registration(interaction.user, real_name)
  └─► if self.thread: await self.thread.edit(archived=True)
```

### Public announcement stays button-free

The public welcome message has no view/button. Its sole purpose is visibility: other members see who joined. All interactive content lives in the private thread.

### `welcome_messages` dict

Currently used to track the channel welcome message for post-registration editing (changes it to "✅ registered"). With the thread path this tracking is no longer needed — thread archival serves the same closure signal. The dict and `msg.edit` flow in `RegistrationModal.on_submit` remain untouched since `welcome_messages.pop(interaction.user.id, None)` returns `None` for thread-path users (nothing was stored), which is safe. The DM fallback never populated it either, so no regression.

### Required bot permissions

- `Create Private Threads` — to call `channel.create_thread` with `ChannelType.private_thread`
- `Manage Threads` — to archive the thread after registration

## Risks / Trade-offs

- **Private threads need Community or boost?** — Private threads are available on all Discord servers as of 2022. No tier requirement.
- **Bot missing Manage Threads permission**: `thread.edit(archived=True)` will raise `discord.Forbidden`. Wrap in `try/except discord.HTTPException` and log a warning — the thread simply stays open until Discord's inactivity archival kicks in. Registration itself still succeeds.
- **Member leaves before registering**: Thread stays open until Discord's auto-archive (default 24h or 1 week depending on server settings). No action needed.
- **High join rate**: Each join creates one thread. At normal classroom scale (tens of students) this is trivial. Thread list grows but each is archived after use.
