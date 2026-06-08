## Why

Discord enforces a 4000-character limit on messages. The `!endclass` attendance report is built as a plain-text block that grows linearly with the number of students. In classes with many students it will silently fail or raise an HTTP exception, and the teacher loses the report entirely. Additionally, teachers need a machine-readable copy of the data for gradebooks or spreadsheets.

## What Changes

- `build_report` continues producing a human-readable summary, but the per-student table is moved into a CSV file instead of a code block
- A `write_report_csv(session, guild)` helper generates a temp CSV file (name, time-in-session, presence status) and returns the file path
- `post_report` sends the CSV as a `discord.File` attachment alongside the text summary
- If the text summary itself exceeds 4000 characters (e.g. very long class name or extreme edge cases), it is split across sequential messages
- Temp file is deleted after the message is sent

## Capabilities

### New Capabilities

- `csv-report-attachment`: Generates a temporary CSV file for each class session and attaches it to the end-of-class report message

### Modified Capabilities

- `attendance-report`: Now attaches a CSV file; text portion is trimmed to the header/stats block only (no inline student table); oversized text is split across multiple messages

## Impact

- Only `bot.py` is touched — `build_report`, a new `write_report_csv`, and `post_report` (extracted from `cmd_endclass`)
- No new dependencies (`csv` and `tempfile` are stdlib)
- Report channel behavior unchanged; fallback path (no channel) also attaches or splits correctly
