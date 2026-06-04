## ADDED Requirements

### Requirement: Teacher can start a presence check
A user with the Teacher role SHALL be able to initiate a presence check during an active class session using `!presence`. The bot SHALL post a message with a "Sign Presence" button that students can click to confirm their active participation.

#### Scenario: Successful presence check start
- **WHEN** a teacher runs `!presence` during an active session
- **THEN** the bot posts a message with a "Sign Presence" interactive button and records the presence check as open

#### Scenario: Presence check rejected — no active session
- **WHEN** a teacher runs `!presence` with no active class session
- **THEN** the bot replies with an error and does not post a button

#### Scenario: Non-teacher tries to start presence check
- **WHEN** a user without the Teacher role runs `!presence`
- **THEN** the bot replies with a permission error

### Requirement: Student can sign presence via command or button
A student SHALL be able to sign their presence either by running `!present` or by clicking the "Sign Presence" button. Each student MAY only sign once per presence check.

#### Scenario: Student signs via command
- **WHEN** a student runs `!present` while a presence check is open
- **THEN** the student is recorded as present for that check and receives a confirmation reply

#### Scenario: Student signs via button
- **WHEN** a student clicks the "Sign Presence" button while a presence check is open
- **THEN** the student is recorded as present and the interaction is acknowledged (ephemeral confirmation)

#### Scenario: Duplicate signature rejected — command
- **WHEN** a student who already signed runs `!present` again
- **THEN** the bot replies with a message indicating they already signed

#### Scenario: Duplicate signature rejected — button
- **WHEN** a student who already signed clicks the "Sign Presence" button again
- **THEN** the bot acknowledges the interaction with an ephemeral error message; no duplicate is recorded

#### Scenario: Sign rejected — no open presence check
- **WHEN** a student runs `!present` or clicks a button with no active presence check
- **THEN** the bot replies with an error indicating no presence check is open

### Requirement: Presence check closes when class ends
When `!endclass` is called, any open presence check SHALL be closed and its button disabled so no further signatures are accepted.

#### Scenario: Button disabled on endclass
- **WHEN** a teacher runs `!endclass` and a presence check is open
- **THEN** the bot edits the presence check message to disable the button and closes the check

#### Scenario: Multiple presence checks per session
- **WHEN** a teacher runs `!presence` more than once during a session
- **THEN** each check is independent; signatures from prior checks are preserved; the new check starts fresh
