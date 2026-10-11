# AI Creative Team for Claude Code

A small team of AI agents that turns raw clips into short vertical videos. One command, and every clip in `inbox/` is cut, captioned and given a cover image, by sub-agents working in parallel. A shared brain remembers your brand rules, and nothing is published without your OK.

Built in the Bekhruz AI video "I Built an AI Agent Team From Scratch".

## What you get

| Piece | File | What it does |
|---|---|---|
| Team charter | `CLAUDE.md` | Who is on the team, the folders, the rules |
| Clip editor | `.claude/agents/clip-editor.md` | Sub-agent: one raw clip in, a finished vertical edit out |
| Brand checker | `.claude/agents/brand-checker.md` | Sub-agent: reviews every edit against your brand rules |
| The command | `.claude/commands/edit-clips.md` | `/edit-clips`: one clip-editor per clip, in parallel, then the check |
| Approvals | `.claude/settings.json` | What the team may do on its own, what it must ask, what it may never do |
| Shared brain | `.mcp.json` + `brain/memory.jsonl` | Memory MCP server holding your brand rules |
| Tools | `tools/cut.py`, `tools/captions.py`, `tools/thumbnail.py`, `tools/frames.py` | Pause and filler removal with vertical reframe, local speech-to-text and word-by-word captions, cover image, contact sheet for checking |

## Setup (once)

You need [Claude Code](https://claude.com/claude-code), ffmpeg, Python 3.10+ and Node.js 18+.

```bash
git clone https://github.com/bekhruztbx/ai-creative-team
cd ai-creative-team
bash tools/setup.sh
```

## Use it

1. Put raw clips (mp4, mov, m4v) in `inbox/`. Tip: make `inbox/` a Google Drive folder with Drive for desktop, and clips you drop on your phone land here.
2. Start Claude Code in this folder: `claude`
3. Type `/edit-clips`

Each clip ends up in `out/<clip-name>/`: `edit.mp4` (vertical, captioned), `cover.jpg`, `captions.srt` and `notes.md` (title, cover text, hook, transcript).

## Teach it your style

Just tell Claude, for example: *"From now on, cover text is red, not yellow."* The rule goes into the shared brain (`brain/memory.jsonl`), and every agent follows it from the next run on. You can also edit the starting rules in that file.

## Safety

- The team may only run the four tools in `tools/`, move clips from `inbox/` to `done/` and write into `out/` (`.claude/settings.json`).
- Deleting files and network tools like `curl` are blocked. Pushing to git asks you first.
- Nothing is uploaded or posted. You review `out/` and publish yourself.

## License

MIT. The Geist font in `tools/fonts/` is under the SIL Open Font License.
