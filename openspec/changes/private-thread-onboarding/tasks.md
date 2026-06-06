## 1. Update `RegistrationView` to accept a thread reference

- [x] 1.1 Add `thread: Optional[discord.Thread] = None` parameter to `RegistrationView.__init__`; call `super().__init__(timeout=None)` and store `self.thread = thread`
- [x] 1.2 In the `set_name` button callback, pass `thread=self.thread` when constructing `RegistrationModal`: `await interaction.response.send_modal(RegistrationModal(thread=self.thread))`

## 2. Update `RegistrationModal` to accept and archive the thread

- [x] 2.1 Add `__init__(self, thread: Optional[discord.Thread] = None)` to `RegistrationModal`; call `super().__init__()` and store `self.thread = thread`
- [x] 2.2 At the end of `on_submit`, after `apply_registration`, add:
  ```python
  if self.thread:
      try:
          await self.thread.edit(archived=True)
      except discord.HTTPException:
          logger.warning("Could not archive registration thread id=%s", self.thread.id)
  ```

## 3. Rewrite `on_member_join` to use private thread

- [x] 3.1 When `WELCOME_CHANNEL_ID` is set and the channel is found:
  - Post a brief public announcement with no button:
    `await channel.send(f"Welcome {member.mention}! Check your private thread to complete registration.")`
  - Create private thread:
    ```python
    thread = await channel.create_thread(
        name=f"Welcome {member.display_name}",
        type=discord.ChannelType.private_thread,
        invitable=False,
    )
    ```
  - Add the new member to the thread: `await thread.add_user(member)`
  - Send the registration form inside the thread:
    ```python
    await thread.send(
        f"Hi {member.mention}! Please register your real name so the teacher can identify you in attendance reports.",
        view=RegistrationView(thread=thread),
    )
    ```
  - Return early (do not fall through to DM)
- [x] 3.2 DM fallback (no `WELCOME_CHANNEL_ID` or channel not found) remains unchanged — `RegistrationView()` is called with no thread argument

## 4. Testing

- [ ] 4.1 Manual test: new member joins with `WELCOME_CHANNEL_ID` set → public announcement appears in welcome channel → private thread created and visible only to that member → thread contains registration message with `[Set My Name]` button → member clicks → modal appears → submits name → `names.json` updated → thread is archived
- [ ] 4.2 Manual test: existing member (not the new joiner) cannot see the private thread in the welcome channel
- [ ] 4.3 Manual test: bot missing `Manage Threads` permission → registration completes normally, warning logged, thread stays open (not archived)
- [ ] 4.4 Manual test: `WELCOME_CHANNEL_ID` unset → DM fallback still works as before
