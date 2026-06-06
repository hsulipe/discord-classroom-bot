## Context

Existing project: single-file `bot.py` (Python + discord.py 2.x), prefix commands. The prior change (`member-real-name-registration`) added `RegistrationModal`, `RegistrationView`, `on_member_join` (DM-based), `!register`, `!setname`, and `names.json` persistence. This change modifies the on-join flow and extends `RegistrationModal.on_submit()`.

## Goals / Non-Goals

**Goals:**
- Post the registration prompt as an ephemeral message in a dedicated welcome channel on member join
- Auto-set server nickname immediately after registration modal is submitted
- Auto-assign a configurable member role immediately after registration modal is submitted
- Keep `!register` and `!setname` consistent — they should also trigger nickname and role updates

**Non-Goals:**
- Removing the `names.json` registry — it remains for report name resolution and as a fallback
- Enforcing that a member must register before they can access other channels (that would require Discord Onboarding or role-gating, out of scope)
- Supporting multiple member roles per registration

## Decisions

### Ephemeral message in welcome channel instead of DM
An ephemeral message (`interaction.response.send_message(..., ephemeral=True)`) is only visible to the target user and automatically disappears. However, ephemeral messages require an interaction context — they cannot be sent proactively.

The workaround: `on_member_join` sends a **normal (non-ephemeral) message** in the welcome channel that contains the "Set My Name" button, then immediately **deletes the message after a short delay** (e.g. 60 seconds) to keep the channel clean. Alternatively, the message can remain visible to all as a public welcome — this is simpler and is the chosen approach. The key UX change is the channel prompt instead of a buried DM.

> **Note:** True ephemeral messages require slash commands or component interactions. A bot cannot send an ephemeral message proactively on join — only in response to an interaction. The on-join message will be a normal channel message visible to everyone, but it mentions the specific member and is deleted after they complete registration (or after a timeout).

### Welcome channel: configurable via `WELCOME_CHANNEL_ID` env var
Same pattern as `REPORT_CHANNEL_ID`. If not set, bot falls back to attempting a DM (preserving existing behavior). This makes the feature opt-in.

### Auto-nickname: `member.edit(nick=real_name)`
Called in `RegistrationModal.on_submit()` after saving to `names.json`. Wrapped in `try/except discord.Forbidden` — the bot cannot set nicknames for members with higher roles (e.g. server owner). Log a warning on failure, do not crash.

### Auto-role: look up role by `MEMBER_ROLE_NAME` in the guild
`discord.utils.get(interaction.guild.roles, name=MEMBER_ROLE_NAME)` — same pattern as `TEACHER_ROLE_NAME`. If the role is not found, log a warning and skip. Wrapped in `try/except discord.Forbidden` — bot role must be above the target role in hierarchy.

### `!register` and `!setname` parity
Both commands now also attempt to set the nickname and assign the role:
- `!register`: author is a `ctx.author` (`discord.Member`) — can call `edit(nick=)` and `add_roles()` directly
- `!setname`: target `member` is already a `discord.Member` — same calls

### Welcome message lifecycle
On join: bot sends `"Welcome @member! Please register your real name → [Set My Name]"` in the welcome channel. After the member submits the modal, the original welcome message is edited to a confirmation (`"✅ @member has registered as Real Name."`) and is not deleted — it serves as a public record. If the member never registers, the message remains as a persistent prompt in the welcome channel.

## Risks / Trade-offs

- **Role hierarchy**: If the bot's role is below the assigned member role, `add_roles()` raises `discord.Forbidden`. Mitigation: log warning, skip role assignment, confirm to user without mentioning role failure.
- **Nickname for server owner**: Discord prevents bots from changing the server owner's nickname. Mitigation: same `Forbidden` catch.
- **Welcome channel not set**: Falls back to DM. If DM also fails, logs warning — member can still use `!register`.
- **Message clutter**: If many members join without registering, the welcome channel accumulates prompts. Mitigation: out of scope for now; a periodic cleanup command could be added later.

## New Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WELCOME_CHANNEL_ID` | No | — | Text channel where on-join registration prompts are posted. Falls back to DM if not set. |
| `MEMBER_ROLE_NAME` | No | — | Role name to assign automatically after registration. No role assigned if not set. |

## Migration Plan

Existing members who already registered via `!register` will not get the role or nickname set retroactively — they can re-run `!register` or the teacher can run `!setname`. No code migration needed; both new env vars are optional.
