## Context

Single-file bot (`bot.py`, Python + discord.py 2.x). There are three registration paths that all funnel into `apply_registration`:

1. **Modal** (`RegistrationModal.on_submit`) — triggered by the "Definir Meu Nome" button
2. **`!register` command** — self-service text command
3. **`!setname` command** — teacher sets a member's name

`apply_registration` calls `member.edit(nick=real_name)`. Discord rejects nicknames longer than 32 chars with HTTP 400, but the bot only catches `discord.Forbidden`, so the 400 bubbles up as an unhandled exception.

## Goals / Non-Goals

**Goals:**
- Prevent the `discord.HTTPException` caused by nicknames > 32 chars
- Show users a hint about the 32-char limit before they submit (modal path)
- Keep the full name in `names.json` for attendance reports — only the Discord nickname is truncated

**Non-Goals:**
- Rejecting names longer than 32 chars entirely (truncation is preferable to rejection)
- Changing how names appear in the attendance report

## Decisions

### Modal: change `max_length` from 80 to 32

`discord.ui.TextInput` enforces `max_length` in Discord's UI: the text field becomes non-enterable past the limit and Discord shows a live character counter (e.g. "28/32"). This is the most direct in-modal warning — no extra label text needed, and it prevents the problem at input time.

The stored name in `names.json` for the modal path will naturally be ≤ 32 chars, matching the applied nickname.

### `apply_registration`: truncate to 32 before `member.edit`

Add `nick = real_name[:32]` before the `member.edit(nick=nick)` call. This is the safety net for all three code paths. For the modal path it is redundant (name is already ≤ 32), but harmless. For `!register` and `!setname`, where teachers or students may pass longer strings, this prevents the exception.

The truncated value is only used for the Discord nickname. `apply_registration` receives the full `real_name` and truncates internally — callers do not need to change.

### `names.json` stores the full name

The full name entered via `!register` or `!setname` (which can exceed 32 chars) is stored as-is in `names.json`. This preserves legibility in attendance reports. Only the nickname applied to Discord is truncated.

### No user-visible truncation notice

A silent truncation is acceptable because:
- Modal path: `max_length=32` prevents any over-length input
- Command path: the success message shows the full saved name; the nickname visible in Discord is the truncated version. If the teacher or student notices the truncation, they can re-register with a shorter name. Adding a conditional message for a rare edge case adds noise for no real gain.

## Code Change Summary

```python
# RegistrationModal.full_name — max_length: 80 → 32
full_name = discord.ui.TextInput(
    label="Nome Completo",
    placeholder="ex.: João Silva",
    min_length=2,
    max_length=32,          # changed from 80
)

# apply_registration — truncate before member.edit
async def apply_registration(member: discord.Member, real_name: str) -> list[str]:
    issues: list[str] = []
    nick = real_name[:32]   # added — Discord nickname limit
    try:
        await member.edit(nick=nick)
    except discord.Forbidden:
        ...
```

## Risks / Trade-offs

- **Teachers entering long names via `!setname`**: The full name is saved in `names.json` correctly. The nickname will be silently truncated to 32 chars. If they notice and object, they can use a shorter version.
- **Report vs. Discord name mismatch**: For names > 32 chars set via commands, the attendance report will show the full name while Discord shows the truncated nickname. This is intentional — reports benefit from full names.
