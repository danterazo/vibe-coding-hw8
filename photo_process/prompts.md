# Project: Photo Process

> - **Files:** photo_process.html
> - **Dates:** 2026-11-04
> - **Defaults:** GitHub Copilot · model TBD
> - **Status:** prototype
> - **Use:** none yet
> - **Reusability:** artifact TBD · prompt pattern TBD
> - **Tags:** single-file-html, canvas, export-import, source-material
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

I built [photo_process.html](photo_process.html) as a local batch image converter. It fits JPEG, PNG, and WebP files without cropping on a white 1500
× 1000 canvas and exports JPEGs tagged at 150 DPI. A browser-generated image verified the output dimensions and 150 × 150 DPI metadata.
