#!/usr/bin/env python3
"""Serve the local Discogs album picker and query a user's collection."""

import argparse
import json
import random
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

APP_DIR = Path(__file__).resolve().parent
API_ROOT = "https://api.discogs.com"
API_USER_AGENT = "discogs-album-picker/1.0"
PER_PAGE = 100
COLLECTION_CACHE_SECONDS = 300
MAX_REQUEST_BYTES = 4096
collection_cache: dict[str, tuple[float, int, list[dict[str, Any]]]] = {}


class PickerError(Exception):
    """An expected API or input error safe to show in the local UI."""


def get_api_page(username: str, token: str, page: int) -> dict[str, Any]:
    encoded_username = quote(username, safe="")
    url = f"{API_ROOT}/users/{encoded_username}/collection/folders/0/releases?per_page={PER_PAGE}&page={page}"
    request = Request(
        url,
        headers={
            "Authorization": f"Discogs token={token}",
            "User-Agent": API_USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in (401, 403):
            raise PickerError("Discogs rejected the username or personal access token.") from error
        if error.code == 429:
            raise PickerError("Discogs rate limit reached. Wait a little, then try again.") from error
        raise PickerError(f"Discogs returned HTTP {error.code}.") from error
    except URLError as error:
        raise PickerError("Could not reach Discogs. Check your internet connection and try again.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PickerError("Discogs returned an unreadable response.") from error


def media_labels(formats: Any) -> list[str]:
    if not isinstance(formats, list):
        return []
    labels = []
    digital_names = {"digital media", "file", "download", "streaming"}
    for format_info in formats:
        if not isinstance(format_info, dict):
            continue
        name = str(format_info.get("name", "")).strip()
        if not name or name.casefold() in digital_names:
            continue
        descriptions = format_info.get("descriptions", [])
        descriptions = [str(value).strip() for value in descriptions if str(value).strip()]
        if name.casefold() == "vinyl":
            if any(value.casefold() == "lp" for value in descriptions):
                name = "LP"
            elif descriptions:
                name = f"Vinyl ({', '.join(descriptions)})"
        quantity = str(format_info.get("qty", "")).strip()
        if quantity and quantity != "1":
            name = f"{quantity} × {name}"
        labels.append(name)
    return labels


def physical_releases(page_data: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for release in page_data.get("releases", []):
        if not isinstance(release, dict):
            continue
        details = release.get("basic_information") or {}
        media = media_labels(details.get("formats"))
        if not media:
            continue
        artists = details.get("artists") or []
        artist_names = [str(artist.get("name", "")).strip() for artist in artists if artist.get("name")]
        results.append(
            {
                "title": str(details.get("title") or "Untitled release"),
                "artist": ", ".join(artist_names) or "Unknown artist",
                "media": media,
                "year": details.get("year") or None,
                "image": details.get("cover_image") or details.get("thumb") or "",
                "url": f"https://www.discogs.com/release/{details.get('id')}" if details.get("id") else "",
            }
        )
    return results


def random_physical_release(
    username: str,
    token: str,
    page_reader=get_api_page,
    rng=random,
) -> dict[str, Any]:
    token = token.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,50}", username):
        raise PickerError("Enter a valid Discogs username.")
    if not token or any(ord(character) < 32 for character in token):
        raise PickerError("Enter a Discogs personal access token.")

    first_page = page_reader(username, token, 1)
    pagination = first_page.get("pagination") or {}
    total_items = int(pagination.get("items") or 0)
    page_count = max(1, int(pagination.get("pages") or 1))
    if total_items == 0:
        raise PickerError("This Discogs collection is empty.")

    cached = collection_cache.get(username)
    if cached is not None and cached[0] > time.monotonic() and cached[1] == total_items:
        cache_is_current = True
        candidates = cached[2]
    else:
        cache_is_current = False
        candidates = physical_releases(first_page)
        for page_number in range(2, page_count + 1):
            candidates.extend(physical_releases(page_reader(username, token, page_number)))
    if not candidates:
        raise PickerError("No non-digital releases were found in this collection.")
    if not cache_is_current:
        collection_cache[username] = (time.monotonic() + COLLECTION_CACHE_SECONDS, total_items, candidates)
    return rng.choice(candidates)


class PickerHandler(BaseHTTPRequestHandler):
    server_version = "DiscogsAlbumPicker/1.0"

    def do_GET(self) -> None:
        if urlsplit(self.path).path not in ("/", "/index.html"):
            self.send_error(404)
            return
        try:
            page = (APP_DIR / "index.html").read_bytes()
        except OSError:
            self.send_error(500, "The app page could not be read.")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/pick":
            self.send_error(404)
            return
        origin = self.headers.get("Origin")
        server = cast(ThreadingHTTPServer, self.server)
        expected_origin = f"http://127.0.0.1:{server.server_port}"
        if origin is not None and origin != expected_origin:
            self.send_json(403, {"error": "Requests must come from this local app."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_REQUEST_BYTES:
                raise PickerError("The request body is missing or too large.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise PickerError("The request was not valid.")
            album = random_physical_release(
                str(payload.get("username", "")).strip(),
                str(payload.get("token", "")),
            )
            self.send_json(200, {"album": album})
        except PickerError as error:
            self.send_json(400, {"error": str(error)})
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "The request was not valid JSON."})
        except Exception:  # noqa: BLE001
            self.send_json(500, {"error": "The picker hit an unexpected error."})

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.log_date_time_string()} {self.address_string()} {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Discogs album picker.")
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), PickerHandler)
    print(f"Discogs Album Picker: http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Discogs Album Picker.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
