# AI Creative Team: one agent, six skills

One Claude Code agent with a library of six skills that turns raw clips into short vertical videos, writes scripts, finds video ideas, writes post copy and learns from your stats. A shared brain remembers your brand rules, and nothing is published without your OK.

Built in the Bekhruz AI series "Build Your AI Team". Episode 4 built this as a team of separate agents. Episode 6 turned every agent into a skill, following Anthropic's advice: don't build agents, build skills.

> Looking for the Episode 4 version, the team of separate sub-agents? It is on the [`episode-4` branch](https://github.com/bekhruztbx/ai-creative-team/tree/episode-4).

## The skills

| Skill | Folder | What it does |
|---|---|---|
| reel | `.claude/skills/reel/` | One raw clip in, a cut, captioned vertical edit out. Its scripts (cut, captions, frames) live in the same folder. |
| pixel | `.claude/skills/pixel/` | The cover image, following your cover rules |
| quill | `.claude/skills/quill/` | Scripts, hooks and voice-overs in your voice |
| radar | `.claude/skills/radar/` | Comments and notes in `inbox/radar/` in, a ranked shortlist of video ideas out |
| relay | `.claude/skills/relay/` | Titles, descriptions, captions and a pinned comment. It never posts. |
| pulse | `.claude/skills/pulse/` | Analytics CSVs in `inbox/stats/` in, lessons for the next script out |

Each skill is a folder with a `SKILL.md`. Claude Code only reads the name and the one-line description of each skill at the start, and opens a skill's full instructions (and its scripts) only when a task needs it.

## Setup (once)

You need [Claude Code](https://claude.com/claude-code), ffmpeg, Python 3.10+ and Node.js 18+.

```bash
git clone https://github.com/bekhruztbx/ai-creative-team
cd ai-creative-team
bash setup.sh
```

## Use it

Start Claude Code in this folder (`claude`) and just ask:

- *"There's a new clip in inbox. Make it a reel."* (uses reel and pixel)
- *"Write a 45-second reel script about …"* (uses quill)
- *"Go through the comments in inbox/radar and tell me what to make next."* (uses radar)
- *"Write the post copy for out/<clip>."* (uses relay)
- *"Here are this month's stats, what worked?"* (uses pulse)

Finished work lands in `out/`. Raw clips move to `done/` after their edit is finished.

## Teach it your style

Tell Claude a preference, for example *"From now on, cover text is red, not yellow."* It goes into the shared brain (`brain/memory.jsonl`) and every skill follows it from then on.

Skills can improve too. When a step keeps going wrong, Claude proposes a change to that skill's `SKILL.md` and shows it to you. Edits to `.claude/skills/` always ask for your OK first (`.claude/settings.json`).

## Safety

- The agent may only run the skill scripts, move clips from `inbox/` to `done/` and write into `out/` (`.claude/settings.json`).
- Deleting files and network tools like `curl` are blocked. Pushing to git asks you first.
- Nothing is uploaded or posted. You review `out/` and publish yourself.
- Installing skills from other people? Read them first, or ask Claude to read one and list every file, command and network call before you use it.

## License

MIT. The Geist font in the skill folders is under the SIL Open Font License.
