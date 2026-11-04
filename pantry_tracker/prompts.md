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

## Prompt 2 (add school-use notes)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Make the photo processor modular, s.t. anyone could put their name and then get attribution in the image. Just make the default name / text box value
"Dante Razo". Add a note to use responsibly as this app (and the others, if they need notes too) is just for school

Aim to have code in one file per project, like the instructions request

### Output 2

Added a school-project note clarifying that best-by dates are reminders rather than food-safety advice. The existing Pantry add/status workflow
remains verified in the browser.
