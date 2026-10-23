---
name: radar
description: Turn comments, notes and links saved in inbox/radar/ into a ranked shortlist of video ideas. Use when Bekhruz asks what to make next, wants ideas, or asks to go through comments.
---

# Radar: what should we make next?

1. **Read the pile.** `ls inbox/radar`, then Read every file (exported comments, notes, links).
2. **Don't repeat.** `mcp__memory__open_nodes` with names ["Ideas"]: ideas already shortlisted or made. Skip them.
3. **Cluster.** Group comments that ask the same thing in different words. Count how many people asked.
4. **Score each cluster** from 1 to 5 on: how many asked, fit with the channel (AI agents, Claude, building in public), and whether it can be shown on screen (a demo beats a talk).
5. **Write** `out/radar/shortlist.md`: the top 3 ideas, each with a working title (under 60 characters), why now (quote 1 or 2 real comments), and the demo you'd show.
6. **Remember.** Save the 3 titles as observations on the brain entity "Ideas" (`mcp__memory__add_observations`; create the entity with `mcp__memory__create_entities` if it doesn't exist).

Reply with the 3 titles, best first.
