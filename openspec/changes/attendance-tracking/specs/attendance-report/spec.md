## ADDED Requirements

### Requirement: Attendance report generated on class end
When a teacher runs `!endclass`, the bot SHALL generate a structured attendance report for the completed session and post it to the configured report channel.

#### Scenario: Report posted to report channel
- **WHEN** `!endclass` is called
- **THEN** the bot posts a formatted attendance report to the channel identified by `REPORT_CHANNEL_ID`

#### Scenario: Report includes session metadata
- **WHEN** the report is generated
- **THEN** it includes the class start time, end time, and total duration

#### Scenario: Report channel not configured
- **WHEN** `REPORT_CHANNEL_ID` is not set or the channel does not exist
- **THEN** the bot logs an error and replies in the command channel indicating the report channel is misconfigured

### Requirement: Report summarizes who was present
The attendance report SHALL list all members who joined the voice channel during the session, noting those who signed a presence check vs. those who were only logged as joined/left.

#### Scenario: Members who joined included in report
- **WHEN** the report is generated
- **THEN** every member who appeared in the session join/leave log is listed

#### Scenario: Presence signatories flagged
- **WHEN** the report is generated and presence checks were held
- **THEN** members who signed at least one presence check are marked as "confirmed present"; others are marked as "joined only"

#### Scenario: No members attended
- **WHEN** no one joined the voice channel during the session
- **THEN** the report indicates zero attendance

### Requirement: Report includes join/leave timeline per member
The report SHALL show each member's total time in the session, derived from join/leave events.

#### Scenario: Single join no leave
- **WHEN** a member joined but never explicitly left before `!endclass`
- **THEN** their leave time is treated as the class end time for duration calculation

#### Scenario: Multiple joins and leaves
- **WHEN** a member joined and left multiple times during the session
- **THEN** all entries are listed or total time is summed — both are acceptable; the report MUST be consistent
