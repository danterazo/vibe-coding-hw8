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
