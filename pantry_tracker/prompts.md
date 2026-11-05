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

## Prompt 3 (increase app scale)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Make the Discogs app and others 125% scale so they're easier to read

### Output 3

Applied a 125% page scale with a smaller minimum layout width for mobile. Browser checks at mobile, tablet, and desktop sizes found no horizontal
overflow.

## Prompt 4 (give each app a visible theme)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Add nice theming to each app. Just a basic color would be fine too as long as its visible. In the camera app, use the full "Canon R50" instead of just
R50

### Output 4

Added a mint-green background and dark green header to Pantry Tracker, retaining its existing layout and controls. Browser checks verified the visible
palette and no header-text overlap or horizontal overflow at desktop and mobile widths.

## Prompt 5 (app setup guide and screenshot)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: diagnostic screenshot
> - **Verified:** agent-tested
> - **Human edits:** none

Make the photo process app's resize feature optional, and the metadata optional as well, but make it so metadata is checked by default.

Create a README with screenshots (zoomed-in, easily visible) for each app in their folder. Include setup instructions, like how to get a Discogs key
and provide it to the app. Include descriptions for each app, too. Any assets used by the README should be under ./APPNAME/assets, for example

Also, add comments, type hints, and named args to the python scripts, per my repo's existing styling instructions. Address all errors such as the
attached

Finally, walk me through how to set up the Discogs app. Can I utilize a .env file that's ignored but still read?

### Output 5

Added a Pantry Tracker README with a close-up screenshot in `assets/`, setup commands, feature descriptions, browser-storage guidance, and safety
notes. With explicit approval, replaced the older parent-folder static server with a Pantry-folder-only server on the same host and port. Verified the
new Pantry URL succeeds and sibling app source paths return 404, without fetching any credential file from the old broad server.
