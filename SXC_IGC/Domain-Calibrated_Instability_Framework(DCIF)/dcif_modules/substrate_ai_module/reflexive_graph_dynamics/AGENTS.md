# Agent Instructions

Read and obey `AI_LAW.md` in this directory before doing anything.

Summary of the hard boundary:

- All file access, searches, commands, temp files, worktrees, and repositories must
  stay under `/home/lenovo/Projects/GI`.
- Never use `/tmp`, `/var/tmp`, or any system temp directory. Use
  `/home/lenovo/Projects/GI/.tmp/` instead.
- Do not fetch external URLs or use web search unless the user explicitly authorizes
  that specific action.
- If a task requires leaving `/home/lenovo/Projects/GI`, stop and report it instead.

`AI_LAW.md` is authoritative; this file is only a pointer.
