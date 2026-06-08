## Context

Single-file bot (`bot.py`). Report generation is currently inline in `cmd_endclass` (lines 428–446). The `build_report` function (lines 132–189) produces a plain-text string with a markdown code block containing the per-student table. No file I/O or multi-message logic exists today. `csv` and `tempfile` are available as stdlib — no new packages needed.

## Goals / Non-Goals

**Goals:**
- Always attach a CSV file with per-student data to the report message
- Keep the text portion to the header/stats block (≤4000 chars in all realistic cases)
- Split any text that exceeds 4000 chars across sequential `channel.send` calls
- Clean up the temp file after sending

**Non-Goals:**
- Persistent CSV storage / archiving
- Changing the CSV format beyond what is useful for a spreadsheet (name, time_seconds, time_formatted, presence_status)
- Changing any other bot commands

## Decisions

### Split `build_report` into two functions
`build_report` will return only the stats header (class name, start/end/duration, student count). A new `write_report_csv(session, guild) -> str` writes a temp file and returns its path. This keeps each function single-purpose and makes it easy to test the CSV independently.

**Alternative considered:** keep one function that returns `(text, csv_path)` tuple — rejected because it complicates the existing call site and mixes concerns.

### Message splitting via a `send_chunked` helper
```python
async def send_chunked(channel, text: str, limit: int = 4000) -> None:
    while text:
        chunk, text = text[:limit], text[limit:]
        await channel.send(chunk)
```
Simple slice-based split. Does not attempt to split on newlines — a single line exceeding 4000 chars is pathological and acceptable to truncate at the boundary. All known realistic inputs (header block) are well under 4000 chars; this is purely a safety net.

**Alternative:** use Discord embeds (6000-char limit) — rejected to avoid changing the existing plain-text format teachers are used to.

### Temp file location and cleanup
`tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")` — `delete=False` required so the file survives past the `with` block for `discord.File` to read it. Cleanup via `os.unlink` in a `finally` block after `channel.send`.

### CSV columns
`name`, `time_seconds`, `time_formatted`, `presence_status`
- `name` — resolved display name (same as `resolve_name`)
- `time_seconds` — raw integer, useful for formulas
- `time_formatted` — `"Xh Ym Zs"` human string
- `presence_status` — `"confirmed"` or `"joined_only"`

### Extract `post_report` from `cmd_endclass`
Current report-sending logic is inlined in `cmd_endclass`. Extract it to `async def post_report(bot, session, guild, fallback_channel)` — takes the channel resolved from `REPORT_CHANNEL_ID` (or falls back to the command channel). This makes the send logic reusable and testable independently.

## Risks / Trade-offs

- **Temp file left on disk if bot crashes between write and send** — risk is a few KB of orphaned files; acceptable for MVP. Mitigation: `finally` block covers the normal path.
- **CSV filename collision** — `tempfile` guarantees unique names; no collision possible.
- **4000-char split mid-word** — `send_chunked` splits on character boundary. Header text is short prose; no word is 4000 chars. Acceptable.

## Migration Plan

No migration needed. Change is entirely additive to `bot.py` — existing `!endclass` behavior is preserved (text report still sent), CSV is added alongside it.
