---
name: pulse
description: Read exported analytics (CSV files in inbox/stats/) and turn them into lessons the other skills use next time. Use when Bekhruz shares stats or asks what worked and what didn't.
---

# Pulse: numbers in, lessons out

1. **Read** every CSV in `inbox/stats/`. Typical columns: title, views, average view duration or retention, click-through rate, likes, comments.
2. **Compare.** Rank the videos by retention first, then by click-through rate. Views alone can mislead.
3. **Find 3 patterns** that are backed by at least two videos each (for example: hook style, length, topic, cover words). Ignore one-offs.
4. **Write** `out/pulse/report.md`: a small table of the videos, the 3 patterns, and one concrete change for the next script.
5. **Teach the team.** Save each pattern as one short observation on the brain entity "Lessons" (`mcp__memory__add_observations`; create it with `mcp__memory__create_entities` if it doesn't exist). The quill skill reads "Lessons" before every script.

Reply with the 3 lessons, one line each.
