## 1. Add stdlib imports

- [x] 1.1 Add `import csv` and `import tempfile` to the top of `bot.py` (they are stdlib — no `requirements.txt` change needed)

## 2. Refactor `build_report` to return header only

- [x] 2.1 Remove the `lines.append("```")` / per-student table block from `build_report` — keep only the header lines (class name, start, end, duration, student count)
- [x] 2.2 Ensure the function still returns `"\n".join(lines)` as before

## 3. Add `write_report_csv`

- [x] 3.1 Implement `write_report_csv(session: SessionState, guild: discord.Guild) -> str`:
  - Re-use the `member_ids`, `member_time`, `all_signatories`, and `resolve_name` logic already present in `build_report`
  - Write columns: `name`, `time_seconds`, `time_formatted`, `presence_status`
  - Use `tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8", newline="")` and return the file path

## 4. Add `send_chunked` helper

- [x] 4.1 Implement `async def send_chunked(channel, text: str, limit: int = 4000) -> None` that slices `text` into `limit`-sized chunks and sends each sequentially

## 5. Extract `post_report` from `cmd_endclass`

- [x] 5.1 Implement `async def post_report(session: SessionState, guild: discord.Guild, report_text: str, csv_path: str, report_channel, fallback_channel) -> None`:
  - Use `send_chunked` for the text portion
  - Attach the CSV via `discord.File(csv_path, filename="relatorio.csv")`
  - Send the file attachment on the last (or only) chunk — or as a separate `channel.send(file=...)` call after the text
  - Delete the temp file in a `finally` block via `os.unlink(csv_path)`
  - Handle missing report channel by falling back to `fallback_channel`

## 6. Update `cmd_endclass` to use new helpers

- [x] 6.1 Replace the inline report-send block in `cmd_endclass` (current lines 428–446) with:
  ```python
  csv_path = write_report_csv(session, ctx.guild)
  report = build_report(session, ctx.guild)
  await post_report(session, ctx.guild, report, csv_path, report_channel, ctx.channel)
  ```

## 7. Manual testing

- [ ] 7.1 Happy path: `!endclass` sends text summary + `relatorio.csv` attachment to report channel
- [ ] 7.2 Verify CSV contains correct columns and one row per student
- [ ] 7.3 Verify temp file is removed after send (check `/tmp` or equivalent)
- [ ] 7.4 Verify no regression: `!endclass` without a configured report channel still sends to the command channel
