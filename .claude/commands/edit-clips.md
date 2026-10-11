---
description: Edit every new clip in inbox/ in parallel, check the results, and report to Bekhruz
---
Edit the new clips in `inbox/`.

1. List the clips: `ls inbox` (mp4, mov, m4v).
2. Start one **clip-editor** sub-agent per clip. Start them all in the same message so they work in parallel. Tell each one its file name.
3. When all of them are done, run the **brand-checker** on `out/`.
4. If the brand-checker flags something, send that clip back to a clip-editor with the exact fix, then check again.
5. Move each finished raw clip: `mv inbox/<file> done/`
6. Report to Bekhruz: a short table (clip, edit length, title, cover text) and the paths. End with: "Nothing is published. Reply OK to approve."

$ARGUMENTS
