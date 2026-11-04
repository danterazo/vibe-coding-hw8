# Project: Pantry Tracker

> - **Files:** pantry_tracker.html
> - **Dates:** 2026-11-04
> - **Defaults:** GitHub Copilot · model TBD
> - **Status:** prototype
> - **Use:** none yet
> - **Reusability:** artifact TBD · prompt pattern TBD
> - **Tags:** single-file-html, productivity, localStorage, export-import
> - **Takeaway:** TBD
> - **Story value:** TBD
> - **Surprises:** TBD

## Prompt 1 (initialize the selected apps)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: CONVENTIONS.md
> - **Verified:** agent-tested
> - **Human edits:** none

Cool, yeah. So lets do:

- pantry_tracker
- photo_process
- discogs_album_picker

Create prompts.md files per the attached conventions, commit as "Init prompts", then go to work developing. Try to automate it all as much as
possible, so when I return from work for lunch, it's all complete or at least in a good state

### Output 1

I built [pantry_tracker.html](pantry_tracker.html) as a single-file pantry inventory. Add, edit, mark used, or remove items; search and filter by
expiry; and export or import a JSON backup. Data stays in browser storage. Browser checks covered adding a near-expiry item, status counters, editing,
filtering, confirmed removal, and persistence after reload.
