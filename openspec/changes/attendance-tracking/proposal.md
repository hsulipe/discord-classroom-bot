## Why

Online classrooms need verifiable attendance beyond passive presence in a voice channel. Teachers need to confirm students are actively engaged and generate records for grading or compliance.

## What Changes

- Add teacher role with class lifecycle commands (`!start`, `!presence`, `!endclass`)
- Add student role with sign-in command (`!present`) and interactive button
- Bot tracks join/leave events during an active class session
- Presence checks let teachers verify active engagement mid-class
- `!endclass` finalizes the session and posts a structured attendance report to a designated report channel
- Students cannot sign presence twice (deduplication enforced)

## Capabilities

### New Capabilities

- `class-session`: Manages the class lifecycle — start, active tracking of join/leave events, and end
- `presence-check`: Mid-class presence verification via command or interactive button with deduplication
- `attendance-report`: Generates and posts end-of-class attendance summary to a configured report channel

### Modified Capabilities

## Impact

- New Discord bot (fresh project — no existing code)
- Requires Discord.py or discord.js with slash/prefix command support and button interaction handling
- Needs persistent in-memory (or lightweight DB) state for active session and presence records
- Requires bot permissions: read messages, send messages, manage messages (remove buttons), read voice state
- Report channel ID must be configurable
