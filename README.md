# Discord Classroom Attendance Bot

A Discord bot for tracking student attendance in voice-channel classes. Teachers control the session lifecycle; students sign presence via command or button. Attendance reports use real names that students register when joining the server.

---

## Features

- **`!start`** — begins a class session and tracks who joins/leaves the voice channel
- **`!presence`** — opens a mid-class presence check with a clickable button
- **`!present`** — students sign presence by command (alternative to the button)
- **`!endclass`** — closes the session and posts an attendance report to a dedicated channel
- **`!register`** — students register their real name so it appears in reports instead of their username
- **`!setname`** — teachers set or correct a student's registered name

---

## Requirements

- Python 3.10+
- A Discord account with permission to create a bot application

---

## 1. Create the Discord Bot Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. Give it a name (e.g. `Classroom Bot`) and click **Create**.
3. In the left sidebar, go to **Bot**.
4. Click **Add Bot** → **Yes, do it!**
5. Under **Token**, click **Reset Token** and copy the token. You will need this later. Keep it secret.
6. Enable the following **Privileged Gateway Intents**:
   - **Server Members Intent**
   - **Message Content Intent**
7. Click **Save Changes**.

---

## 2. Invite the Bot to Your Server

1. In the Developer Portal, go to **OAuth2 → URL Generator**.
2. Under **Scopes**, select `bot`.
3. Under **Bot Permissions**, select:
   - Read Messages / View Channels
   - Send Messages
   - Read Message History
   - Use Slash Commands
   - Manage Nicknames *(required for auto-setting member nicknames on registration)*
   - Manage Roles *(required for auto-assigning the member role on registration)*
   - Connect *(optional, not required but harmless)*
4. Copy the generated URL and open it in your browser.
5. Select your server and click **Authorize**.

---

## 3. Configure Your Server

### Create the Teacher role

The bot distinguishes teachers from students by Discord role name.

1. In your server, go to **Server Settings → Roles → Create Role**.
2. Name it exactly `Teacher` (case-sensitive, matches the default in `.env`).
3. Assign the `Teacher` role to all instructors.

> To use a different role name, set `TEACHER_ROLE_NAME` in your `.env` file (see step 4).

### Create the report channel

The bot posts the attendance report to a dedicated text channel at the end of each class.

1. Create a text channel (e.g. `#attendance-reports`).
2. Copy its ID: right-click the channel → **Copy Channel ID**.
   *(Enable Developer Mode under User Settings → Advanced if you don't see this option.)*
3. Paste the ID into `REPORT_CHANNEL_ID` in your `.env` file.

---

## 4. Local Setup

```bash
# Clone or copy the project, then install dependencies
pip install -r requirements.txt

# Copy the example env file
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
DISCORD_TOKEN=your_bot_token_here
REPORT_CHANNEL_ID=123456789012345678
TEACHER_ROLE_NAME=Teacher
WELCOME_CHANNEL_ID=123456789012345678
MEMBER_ROLE_NAME=Student
```

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | Yes | Bot token from the Developer Portal |
| `REPORT_CHANNEL_ID` | Yes | ID of the text channel to receive reports |
| `TEACHER_ROLE_NAME` | No | Discord role name for teachers (default: `Teacher`) |
| `WELCOME_CHANNEL_ID` | No | ID of the channel where on-join registration prompts are posted. Falls back to a DM if not set. |
| `MEMBER_ROLE_NAME` | No | Role name automatically assigned to a member after they complete registration (e.g. `Student`). No role is assigned if not set. |

---

## 5. Run the Bot

```bash
python3 bot.py
```

You should see a log line like:

```
2024-01-01 12:00:00 INFO Logged in as Classroom Bot (id=123456789)
```

---

## Usage

### Name Registration

Attendance reports show each student's **registered real name** instead of their Discord username or nickname. There are three ways a name can be registered:

1. **On join (automatic):** When a new member joins the server, the bot posts a welcome message in the configured welcome channel with a **Set My Name** button. Clicking it opens a popup form where they type their full name. Once submitted:
   - Their server **nickname is automatically updated** to the registered name
   - The configured **member role is automatically assigned** (e.g. `Student`)
   - The welcome message is updated to a confirmation

   > If `WELCOME_CHANNEL_ID` is not set, the bot sends the prompt as a DM instead.

2. **`!register` command (self-service):** Any member can register or update their name at any time by typing in any channel:
   ```
   !register John Silva
   ```
   The bot saves the name, updates the server nickname, and assigns the member role.

3. **`!setname` command (teacher override):** A teacher can set a name on behalf of any member — useful when a student needs a correction:
   ```
   !setname @username John Silva
   ```
   The bot updates the name, nickname, and role, then notifies the student via DM.

> Names are saved to `names.json` and persist across bot restarts. If a student has not registered, the report falls back to their Discord display name.

---

### Command Reference

#### Teacher commands

| Command | Arguments | Description |
|---|---|---|
| `!start` | — | Start a class session. You must be in a voice channel. The bot records all students already present and begins tracking joins/leaves. Only one session can be active per server at a time. |
| `!presence` | — | Open a presence check. Posts a **✅ Sign Presence** button and accepts `!present` until the session ends or a new `!presence` is called (which closes the previous one). |
| `!endclass` | — | End the class. Closes any open presence check and posts the full attendance report to the configured report channel. |
| `!setname` | `@member` `Full Name` | Set or correct the registered name for a specific member. Requires the Teacher role. Sends a DM to the affected member notifying them of the change. |

#### Student commands

| Command | Arguments | Description |
|---|---|---|
| `!present` | — | Sign your presence during an open presence check. Can only be used once per check. |
| `!register` | `Full Name` | Register your real name. This name will appear in all future attendance reports. Can be used at any time to register or update your name. |

> Students can only sign once per presence check. Attempting to sign twice returns an error message visible only to them.

---

## Attendance Report

When `!endclass` is called, the bot posts a report like this to the configured report channel:

```
**Attendance Report**
Start  : 2024-01-15 10:00:00 UTC
End    : 2024-01-15 11:30:00 UTC
Duration: 1h 30m 0s
Total students: 3

Name                     Time in session    Presence
------------------------------------------------------------
John Silva               1h 28m 12s         Confirmed present
Maria Oliveira           45m 3s             Joined only
Carlos Souza             1h 30m 0s          Confirmed present
```

- **Confirmed present** — student signed at least one presence check (via button or `!present`)
- **Joined only** — student was in the voice channel but did not sign any presence check

---

## Notes

- Only one class session can be active per server at a time. Run `!endclass` before starting a new one.
- Session state is held in memory. If the bot restarts mid-class, the session is lost.
- The bot tracks the voice channel the teacher was in when `!start` was called. Students in other channels are not tracked.
- `names.json` is created automatically on first registration. If the file is deleted, names are lost and reports fall back to Discord display names until students re-register.
- Students who joined the server before the bot was deployed will not receive an on-join welcome prompt. Ask them to run `!register Full Name` in any channel before the first class.
- The bot's role must be **above the member role** in the server role hierarchy for automatic role assignment to work. Adjust role order under **Server Settings → Roles**.
- The bot cannot change the server owner's nickname — this is a Discord limitation. The owner can set their own name via `!register`.
