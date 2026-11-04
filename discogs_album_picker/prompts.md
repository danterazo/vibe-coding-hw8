# Project: discogs-album-picker

> - **Files:** app.py, index.html
> - **Dates:** 2026-11-04
> - **Defaults:** GitHub Copilot · model TBD
> - **Status:** prototype
> - **Use:** none yet
> - **Reusability:** artifact TBD · prompt pattern TBD
> - **Tags:** productivity, source-material
> - **Takeaway:** TBD
> - **Story value:** TBD
> - **Surprises:** TBD

## Prompt 1 (Discogs album picker)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Oh, let's make a small app that hits the Discogs API and returns a random non-digital album to put on from my collection. Call it
"discogs-album-picker". Ensure you show the album art, artist, type of media (e.g. CD, cassette, LP) as well. Just initialize prompts.md files for
this and the other apps.

### Output 1

I built [app.py](app.py) and [index.html](index.html) as a local Discogs picker. Enter your username and personal access token to choose a random
physical release; its cover, artist, title, year, and media formats are shown. The server scans all collection pages and caches release data in memory
for five minutes, while revalidating the token on each pick. Seven credential-free tests pass, and the UI passed a mocked browser check. Live account
access remains unverified because no Discogs credentials were available.

## Prompt 2 (initialize and develop the selected apps)

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

### Output 2

I completed the three selected apps and verified their core workflows. See the app-specific outputs in the Pantry Tracker and Photo Process logs; the
Discogs picker implementation and live-API caveat are documented above.

## Prompt 3 (school-use notes)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Make the photo processor modular, s.t. anyone could put their name and then get attribution in the image. Just make the default name / text box value
"Dante Razo". Add a note to use responsibly as this app (and the others, if they need notes too) is just for school

Aim to have code in one file per project, like the instructions request

### Output 3

Added a school-project note reminding users to access only collections they are authorized to use. The Discogs token remains in the current tab and is
not saved.

## Prompt 4 (keep Python and HTML separate)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Actually, it seems messier with just one file, so have a python file and HTML one but no test file for the Discogs app.

### Output 4

Kept the Python server and HTML interface as separate runtime files and removed the test module. The existing seven-test suite passed before removal.

## Prompt 5 (media filters and iconography)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Add iconography to the Discogs page. Make it more obvious that something is a CD, cassette, or LP, or whatever. Use title case wherever applicable.
Add a filter feature with checkboxes for different media types — support digital media, but have it unchecked by default.

## Output 5

Added icon-and-label media filters for LP, Vinyl, CD, Cassette, DVD, Blu-ray, Other Physical, and Digital. Physical categories start checked and
Digital starts unchecked. The backend now keeps digital releases available and filters picks using the selected media types. Mocked browser checks
verified the submitted filters and rendered format chips; credential-free backend checks covered Digital, CD, Cassette, and LP selection. The Discogs
form and media labels use Title Case.

## Prompt 6 (load Discogs credentials from .env)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

I migrated the token to ".env". Give users the option to enter it on the website or, if .env is detected with DISCOGS_PAT, read that in and blank out
the field on the website since you already have a token. I also have DISCOGS_USERNAME.

### Output 6

The server reads `DISCOGS_PAT` and `DISCOGS_USERNAME` from the process environment or the local `.env`, including the existing colon-separated format.
`/api/config` returns only the username and whether a PAT is configured, never the PAT. A configured PAT leaves the browser field blank and disabled;
otherwise manual token entry remains available. The username is prefilled when configured. Browser checks confirmed the configured state without
displaying credential values.
