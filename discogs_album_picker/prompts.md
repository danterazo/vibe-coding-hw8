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
`/api/config` returns only the username, source label, and configured boolean; it never returns the PAT. A configured PAT leaves the browser field
blank and disabled; otherwise manual token entry remains available. The username is prefilled when configured. Browser checks confirmed the configured
state without displaying credential values.

## Prompt 7 (show configured PAT status)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Or, you could just have dots in the PAT field with an arbitrary number of them to show that it was read from the env. Make sure that the user knows,
somewhere somehow, that this was configured in `.env`

### Output 7

The PAT field stays blank and disabled when a server-side PAT is configured, with a dot mask as its placeholder and a note that identifies the source
as local `.env`. The config endpoint returns only the username, source label, and configured boolean; it never returns the PAT. Browser checks
confirmed the empty field, disabled state, mask, and note.

## Prompt 8 (show Japanese native names)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

For Japanese albums and artist, place their native name (kanji, kana) in parenthesis after the romaji name

### Output 8

Discogs artist name variations containing Japanese script are now appended in parentheses after the romanized artist name. When native title variation
fields are present, they are displayed the same way after the romanized album title. Existing names that already contain Japanese are left as-is; when
Discogs supplies no native variant, the available title/name is preserved without guessing a translation.

## Prompt 9 (make cassette filtering easier)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Why can't I filter on cassettes? My library has plenty of cassettes, e.g. George Strait, Tokenai Namae, etc.

### Output 9

The checkbox filter included any checked type, and all physical types start checked, so selecting Cassette alone did not narrow the pool. Added
one-click Physical Only, Cassette Only, and All Media presets while retaining individual checkboxes. Verified Cassette Only submits only `cassette`
and returns a cassette-format result; the shortcut controls fit on mobile.

## Prompt 10 (use only the existing media checkboxes)

> - **Tool:** GitHub Copilot · model TBD · 2026-11-04
> - **Session:** continued · attached: none
> - **Verified:** agent-tested
> - **Human edits:** none

Why do you need these additional filters? Just fix the filters that are already there. That way if I want every type of media, I just leave the
defaults. If I only want cassettes, I uncheck everything except cassettes

### Output 10

Removed the extra preset buttons and kept only the existing media checkboxes. Physical formats remain checked by default and Digital remains
unchecked; the helper text explains that checked formats are included. Browser verification confirmed the Cassette-only checkbox selection submits
only `cassette` and renders a cassette-format result.
