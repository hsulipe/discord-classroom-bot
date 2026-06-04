## ADDED Requirements

### Requirement: Teacher can start a class session
A user with the Teacher role SHALL be able to start a class session in their current voice channel using `!start`. Only one active session per guild is allowed at a time. The bot SHALL begin tracking voice join/leave events for that channel upon session start.

#### Scenario: Successful class start
- **WHEN** a teacher runs `!start` with no active session in the guild
- **THEN** the bot creates a new session linked to the teacher's current voice channel, confirms with a message, and begins tracking join/leave events

#### Scenario: Start rejected — no active voice channel
- **WHEN** a teacher runs `!start` while not connected to a voice channel
- **THEN** the bot replies with an error message and does not create a session

#### Scenario: Start rejected — session already active
- **WHEN** a teacher runs `!start` while a session is already active in the guild
- **THEN** the bot replies with an error indicating a class is already in progress

#### Scenario: Non-teacher tries to start
- **WHEN** a user without the Teacher role runs `!start`
- **THEN** the bot replies with a permission error and does not create a session

### Requirement: Bot tracks voice join and leave events during active session
While a class session is active, the bot SHALL record a timestamped entry for every member who joins or leaves the tracked voice channel.

#### Scenario: Student joins during active session
- **WHEN** a student joins the tracked voice channel while a session is active
- **THEN** a join event with the member ID and timestamp is appended to the session log

#### Scenario: Student leaves during active session
- **WHEN** a student leaves the tracked voice channel while a session is active
- **THEN** a leave event with the member ID and timestamp is appended to the session log

#### Scenario: Voice event ignored when no session active
- **WHEN** any member joins or leaves a voice channel and no session is active
- **THEN** no event is recorded

### Requirement: Teacher can end the class session
A user with the Teacher role SHALL be able to end the active class session using `!endclass`. Ending the session SHALL disable any open presence check and trigger the attendance report.

#### Scenario: Successful class end
- **WHEN** a teacher runs `!endclass` with an active session
- **THEN** the session is marked complete, any active presence check button is disabled, and the attendance report is generated and posted

#### Scenario: End rejected — no active session
- **WHEN** a teacher runs `!endclass` with no active session
- **THEN** the bot replies with an error indicating no class is in progress

#### Scenario: Non-teacher tries to end
- **WHEN** a user without the Teacher role runs `!endclass`
- **THEN** the bot replies with a permission error
