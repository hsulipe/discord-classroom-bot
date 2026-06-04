# Discord Classroom Attendance Bot

A Discord bot for tracking student attendance in voice-channel classes. Teachers control the session lifecycle; students sign presence via command or button.

---

## Features

- **`!start`** — begins a class session and tracks who joins/leaves the voice channel
- **`!presence`** — opens a mid-class presence check with a clickable button
- **`!present`** — students sign presence by command (alternative to the button)
- **`!endclass`** — closes the session and posts an attendance report to a dedicated channel

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
```

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | Yes | Bot token from the Developer Portal |
| `REPORT_CHANNEL_ID` | Yes | ID of the text channel to receive reports |
| `TEACHER_ROLE_NAME` | No | Discord role name for teachers (default: `Teacher`) |

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

### For teachers

| Command | Description |
|---|---|
| `!start` | Start a class. You must be in a voice channel. Bot records everyone already present. |
| `!presence` | Open a presence check. Students have 30 minutes or until `!endclass`. |
| `!endclass` | End the class. Closes any open presence check and posts the attendance report. |

### For students

| Command | Description |
|---|---|
| `!present` | Sign your presence during an open presence check. |
| Button | Click the **✅ Sign Presence** button posted by `!presence`. |

> Students can only sign once per presence check. Attempting to sign twice returns an error.

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
Alice                    1h 28m 12s         Confirmed present
Bob                      45m 3s             Joined only
Carol                    1h 30m 0s          Confirmed present
```

- **Confirmed present** — student signed at least one presence check
- **Joined only** — student was in the voice channel but did not sign any presence check

---

## Notes

- Only one class session can be active per server at a time. Run `!endclass` before starting a new one.
- Session state is held in memory. If the bot restarts mid-class, the session is lost.
- The bot tracks the voice channel the teacher was in when `!start` was called. Students in other channels are not tracked.
