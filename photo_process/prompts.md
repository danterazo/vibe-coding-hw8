# Project: Photo Process

> - **Files:** app.py, photo_process.html
> - **Dates:** 2026-11-04
> - **Defaults:** GitHub Copilot · model TBD
> - **Status:** prototype
> - **Use:** none yet
> - **Reusability:** artifact TBD · prompt pattern TBD
> - **Tags:** canvas, export-import, source-material
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

## Prompt 2 (match shared ExifTool metadata)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Okay, try again for the piecemeal commits. Then for the photo processing tool, look at my exiftool processing script in my common repo(s) and apply
those same metadata changes, i.e. "Dante Razo" as the author.

### Output 2

Updated JPEG exports to match the shared `process-photos.sh` metadata: EXIF Artist and Copyright, XMP Creator, AttributionName, CaptionWriter, Credit,
Title, PreservedFileName, and `Processed=True`. ExifTool verified every field on a browser-generated JPEG, including the exact `© Dante Razo`
copyright. The 1500 × 1000 dimensions and 150 DPI density remain intact; the shared script was not changed.

## Prompt 3 (editable attribution and school-use notes)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Make the photo processor modular, s.t. anyone could put their name and then get attribution in the image. Just make the default name / text box value
"Dante Razo". Add a note to use responsibly as this app (and the others, if they need notes too) is just for school

Aim to have code in one file per project, like the instructions request

### Output 3

Added an editable author/credit field defaulting to `Dante Razo`. Its value populates EXIF Artist and Copyright plus XMP Creator, AttributionName,
CaptionWriter, and Credit; the title, preserved filename, and processed flag remain. XML values are escaped. ExifTool verified a custom `Alex & Co`
name in every author field. Added a visible reminder to process only images the user has permission to edit and that attribution is user-provided.

## Prompt 4 (increase app scale)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Make the Discogs app and others 125% scale so they're easier to read

### Output 4

Applied a 125% page scale with a smaller minimum layout width for mobile. Browser checks at mobile, tablet, and desktop sizes found no horizontal
overflow; the author field and school-use note remain visible.

## Prompt 5 (give each app a visible theme)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Add nice theming to each app. Just a basic color would be fine too as long as its visible. In the camera app, use the full "Canon R50" instead of just
R50

### Output 5

Added a rose background, red header, and matching primary controls to Photo Process. The header now says "Canon R50 sharing preset" with readable
white text. Browser checks verified the label and no header-text overlap or horizontal overflow at desktop and mobile widths.

## Prompt 6 (save beside the HTML)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: photo_process.html
> - **Verified:** agent-tested
> - **Human edits:** none

For the photo processing app, save output to ./output/ relative to the HTML file

### Output 6

Processed JPEGs now save automatically to `photo_process/output/` when using the approved local Python server. Duplicate names receive numbered
suffixes instead of overwriting existing files. The app shows the output destination and each saved path; direct/static HTML previews retain browser
downloads.

Start the server from this directory with `python app.py --port 8771`, then open `http://127.0.0.1:8771/`. The preview is running there for this
session; port 8770 was already occupied and was left untouched. Generated outputs are ignored by Git.

Browser and disk checks verified two saved JPEGs, 1500 by 1000 dimensions, 150 DPI, preserved attribution, duplicate-name handling, unsafe-request
rejection, and mobile layout. Two generated verification JPEGs named `photo-output-check-1500x1000-150dpi.jpg` and
`photo-output-check-1500x1000-150dpi-2.jpg` remain in the output folder for inspection.

## Prompt 7 (optional processing and app documentation)

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

### Output 7

Added independent Resize and Add Metadata checkboxes with metadata checked by default; resizing also starts checked to preserve the existing preset.
All four combinations passed real JPEG dimension and attribution-tag checks. A UI-level save with both off preserved the 321 by 123 source dimensions
and required no author. Added this app's README and readable screenshot under `assets/`, and documented setup, output saving, option behavior, and
metadata limits. Added comments and named calls to the Python save server and verified its diagnostics. Servers were restarted with approval.
