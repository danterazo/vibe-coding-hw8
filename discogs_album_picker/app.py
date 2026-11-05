#!/usr/bin/env python3
"""Serve the local Discogs album picker and query a user's collection."""

import argparse
import hashlib
import json
import os
import random
import re
import shlex
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

APP_DIR = Path(__file__).resolve().parent
API_ROOT = 'https://api.discogs.com'
API_USER_AGENT = 'discogs-album-picker/1.0'
PER_PAGE = 100
COLLECTION_CACHE_SECONDS = 300
MAX_REQUEST_BYTES = 4096
SUPPORTED_MEDIA_TYPES = {
    'lp',
    'vinyl',
    'cd',
    'cassette',
    'dvd',
    'blu-ray',
    'other-physical',
    'digital',
}
DIGITAL_FORMAT_NAMES = {'digital media', 'file', 'download', 'streaming'}
JAPANESE_TEXT = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]')
collection_cache: dict[str, tuple[float, int, list[dict[str, Any]]]] = {}
master_image_cache: dict[str, str] = {}
catalog_cache: dict[str, tuple[float, dict[str, Any]]] = {}
identity_cache: dict[str, tuple[float, str]] = {}


def load_local_environment(path: Path) -> dict[str, str]:
    """Read only the two supported settings without exposing other local secrets."""
    values = {}
    try:
        with path.open(encoding='utf-8') as env_file:
            for line in env_file:
                entry = line.strip()
                if not entry or entry.startswith('#'):
                    continue
                if entry.startswith('export '):
                    entry = entry[7:].lstrip()
                key, separator, raw_value = entry.partition('=')
                if not separator:
                    key, separator, raw_value = entry.partition(':')
                key = key.strip()
                if not separator or key not in {'DISCOGS_PAT', 'DISCOGS_USERNAME'}:
                    continue
                try:
                    parts = shlex.split(raw_value, comments=True, posix=True)
                except ValueError:
                    continue
                values[key] = ' '.join(parts)
    except OSError:
        return {}
    return values


# process settings override the ignored file; neither source is sent to the browser.
LOCAL_ENV = load_local_environment(path=APP_DIR / '.env')
DISCOGS_USERNAME = (os.environ.get('DISCOGS_USERNAME') or LOCAL_ENV.get('DISCOGS_USERNAME', '')).strip()
PROCESS_DISCOGS_PAT = os.environ.get('DISCOGS_PAT', '').strip()
FILE_DISCOGS_PAT = LOCAL_ENV.get('DISCOGS_PAT', '').strip()
DISCOGS_PAT = PROCESS_DISCOGS_PAT or FILE_DISCOGS_PAT
DISCOGS_PAT_SOURCE = 'process environment' if PROCESS_DISCOGS_PAT else 'local .env' if FILE_DISCOGS_PAT else ''


class PickerError(Exception):
    """An expected API or input error safe to show in the local UI."""


def get_api_page(username: str, token: str, page: int) -> dict[str, Any]:
    encoded_username = quote(username, safe='')
    url = f'{API_ROOT}/users/{encoded_username}/collection/folders/0/releases?per_page={PER_PAGE}&page={page}'
    request = Request(
        url=url,
        headers={
            'Authorization': f'Discogs token={token}',
            'User-Agent': API_USER_AGENT,
            'Accept': 'application/json',
        },
    )
    try:
        with urlopen(url=request, timeout=20) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        if error.code in (401, 403):
            raise PickerError('Discogs rejected the username or personal access token.') from error
        if error.code == 429:
            raise PickerError('Discogs rate limit reached. Wait a little, then try again.') from error
        raise PickerError(f'Discogs returned HTTP {error.code}.') from error
    except URLError as error:
        raise PickerError('Could not reach Discogs. Check your internet connection and try again.') from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PickerError('Discogs returned an unreadable response.') from error


def media_descriptors(formats: Any) -> list[dict[str, str]]:
    if not isinstance(formats, list):
        return []
    descriptors = []
    for format_info in formats:
        if not isinstance(format_info, dict):
            continue
        raw_name = str(format_info.get('name', '')).strip()
        if not raw_name:
            continue
        descriptions = format_info.get('descriptions', [])
        descriptions = [str(value).strip() for value in descriptions if str(value).strip()]
        name = raw_name.casefold()
        description_set = {value.casefold() for value in descriptions}
        if name in DIGITAL_FORMAT_NAMES:
            media_type = 'digital'
            label = 'Digital'
            if descriptions:
                label = f'Digital ({", ".join(descriptions)})'
        elif name == 'vinyl' and 'lp' in description_set:
            media_type = 'lp'
            label = 'LP'
        elif name == 'vinyl':
            media_type = 'vinyl'
            label = 'Vinyl'
        elif name in {'cd', 'compact disc'}:
            media_type = 'cd'
            label = 'CD'
        elif 'cassette' in name or name in {'tape', 'compact cassette'}:
            media_type = 'cassette'
            label = 'Cassette'
        elif 'blu-ray' in name or 'blu ray' in name:
            media_type = 'blu-ray'
            label = 'Blu-ray'
        elif 'dvd' in name:
            media_type = 'dvd'
            label = 'DVD'
        else:
            media_type = 'other-physical'
            label = raw_name.title()
        quantity = str(format_info.get('qty', '')).strip()
        if quantity and quantity != '1':
            label = f'{quantity} × {label}'
        descriptors.append({'type': media_type, 'label': label})
    return descriptors


def append_native_name(romanized: str, native: Any) -> str:
    native_name = str(native or '').strip()
    if not romanized or not JAPANESE_TEXT.search(native_name):
        return romanized
    if JAPANESE_TEXT.search(romanized) or native_name.casefold() in romanized.casefold():
        return romanized
    return f'{romanized} ({native_name})'


def native_title(details: dict[str, Any], title: str) -> str:
    romanized_title = str(details.get('title_romaji') or details.get('romaji_title') or title).strip()
    native_value = next(
        (details.get(key) for key in ('native_title', 'title_native', 'title_anv', 'original_title', 'title_variation') if details.get(key)),
        None,
    )
    source_title = str(details.get('title') or '').strip()
    if native_value is None and source_title != romanized_title and JAPANESE_TEXT.search(source_title):
        native_value = source_title
    return append_native_name(romanized=romanized_title, native=native_value)


def collection_releases(page_data: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for release in page_data.get('releases', []):
        if not isinstance(release, dict):
            continue
        details = release.get('basic_information') or {}
        media = media_descriptors(formats=details.get('formats'))
        if not media:
            continue
        artists = details.get('artists') or []
        artist_names = []
        for artist in artists:
            if not isinstance(artist, dict):
                continue
            name = str(artist.get('name', '')).strip()
            if name:
                artist_names.append(append_native_name(romanized=name, native=artist.get('anv')))
        title = str(details.get('title') or 'Untitled release')
        results.append(
            {
                'release_id': details.get('id'),
                'collection_instance_id': release.get('instance_id'),
                'title': native_title(details=details, title=title),
                'artist': ', '.join(artist_names) or 'Unknown artist',
                'artist_id': next(
                    (artist.get('id') for artist in artists if isinstance(artist, dict) and artist.get('id') and str(artist['id']) != '194'),
                    None,
                ),
                'media_types': sorted({medium['type'] for medium in media}),
                'media': media,
                'year': details.get('year') or None,
                'image': details.get('cover_image') or details.get('thumb') or '',
                'master_id': details.get('master_id') or None,
                'url': f'https://www.discogs.com/release/{details.get("id")}' if details.get('id') else '',
            }
        )
    return results


def master_cover_image(master_id: Any, token: str) -> str:
    """Use master artwork only as a fallback, never as a replacement release."""
    master_key = str(master_id or '').strip()
    if not master_key.isdigit():
        return ''
    if master_key in master_image_cache:
        return master_image_cache[master_key]
    request = Request(
        url=f'{API_ROOT}/masters/{master_key}',
        headers={
            'Authorization': f'Discogs token={token}',
            'User-Agent': API_USER_AGENT,
            'Accept': 'application/json',
        },
    )
    try:
        with urlopen(url=request, timeout=20) as response:
            master = json.loads(response.read().decode('utf-8'))
    except HTTPError, URLError, UnicodeDecodeError, json.JSONDecodeError:
        master_image_cache[master_key] = ''
        return ''
    image_url = ''
    for image in master.get('images') or []:
        if not isinstance(image, dict):
            continue
        image_url = image.get('uri') or image.get('resource_url') or image.get('uri150')
        if isinstance(image_url, str) and image_url.startswith(('https://', 'http://')):
            break
        image_url = ''
    master_image_cache[master_key] = image_url
    return image_url


def catalog_details(resource: str, identifier: Any, token: str) -> dict[str, Any] | None:
    """Share short-lived release and artist details across repeated selections."""
    catalog_id = str(identifier or '').strip()
    if resource not in {'releases', 'artists'} or not catalog_id.isdigit():
        return None
    cache_key = f'{resource}/{catalog_id}'
    cached = catalog_cache.get(cache_key)
    if cached is not None and cached[0] > time.monotonic():
        return cached[1]
    request = Request(
        url=f'{API_ROOT}/{cache_key}',
        headers={
            'Authorization': f'Discogs token={token}',
            'User-Agent': API_USER_AGENT,
            'Accept': 'application/json',
        },
    )
    try:
        with urlopen(url=request, timeout=20) as response:
            details = json.loads(response.read().decode('utf-8'))
    except OSError, UnicodeDecodeError, json.JSONDecodeError:
        return None
    if not isinstance(details, dict):
        return None
    catalog_cache[cache_key] = (time.monotonic() + COLLECTION_CACHE_SECONDS, details)
    return details


def release_tracklist(release_id: Any, token: str) -> list[dict[str, Any]] | None:
    details = catalog_details(resource='releases', identifier=release_id, token=token) or {}
    tracks = details.get('tracklist')
    return [track for track in tracks if isinstance(track, dict)] if isinstance(tracks, list) else None


def artist_background(artist_id: Any, token: str) -> dict[str, str] | None:
    details = catalog_details(resource='artists', identifier=artist_id, token=token) or {}
    profile = details.get('profile')
    if not isinstance(profile, str) or not profile.strip():
        return None
    summary = profile.strip().splitlines()[0]
    summary = re.sub(r'\[(?:a|l|r|m)=([^\]]+)\]', r'\1', summary)
    summary = re.sub(r'\[/?(?:b|i|u|url)(?:=[^\]]+)?\]', '', summary)
    summary = ' '.join(summary.split())
    if len(summary) > 320:
        summary = summary[:317].rsplit(' ', 1)[0] + '...'
    return {'name': str(details.get('name') or ''), 'summary': summary, 'url': f'https://www.discogs.com/artist/{artist_id}'}


def load_collection(
    username: str,
    token: str,
    page_reader: Callable[[str, str, int], dict[str, Any]] = get_api_page,
) -> list[dict[str, Any]]:
    """Load every collection page while preserving the injected reader contract."""
    token = token.strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}', username):
        raise PickerError('Enter a valid Discogs username.')
    if not token or any(ord(character) < 32 for character in token):
        raise PickerError('Enter a Discogs personal access token.')
    first_page = page_reader(username, token, 1)
    pagination = first_page.get('pagination') or {}
    total_items = int(pagination.get('items') or 0)
    page_count = max(1, int(pagination.get('pages') or 1))
    if total_items == 0:
        raise PickerError('This Discogs collection is empty.')

    cached = collection_cache.get(username)
    if cached is not None and cached[0] > time.monotonic() and cached[1] == total_items:
        cache_is_current = True
        candidates = cached[2]
    else:
        cache_is_current = False
        candidates = collection_releases(page_data=first_page)
        for page_number in range(2, page_count + 1):
            candidates.extend(collection_releases(page_data=page_reader(username, token, page_number)))
    if not candidates:
        raise PickerError('No releases with supported media formats were found in this collection.')
    if not cache_is_current:
        collection_cache[username] = (time.monotonic() + COLLECTION_CACHE_SECONDS, total_items, candidates)
    return candidates


def collection_inventory(
    username: str,
    token: str,
    page_reader: Callable[[str, str, int], dict[str, Any]] = get_api_page,
) -> dict[str, Any]:
    candidates = load_collection(username=username, token=token, page_reader=page_reader)
    counts = {}
    for release in candidates:
        for media_type in release['media_types']:
            counts[media_type] = counts.get(media_type, 0) + 1
    return {'total': len(candidates), 'media_types': sorted(counts), 'media_counts': counts}


def authenticated_collection_user(username: str, token: str) -> str:
    """Restrict selection to the token owner's collection, not another public account."""
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}', username):
        raise PickerError('Enter a valid Discogs username.')
    token = token.strip()
    if not token or any(ord(character) < 32 for character in token):
        raise PickerError('Enter a Discogs personal access token.')
    key = hashlib.sha256(token.encode('utf-8')).hexdigest()
    cached = identity_cache.get(key)
    if cached is not None and cached[0] > time.monotonic():
        owner = cached[1]
    else:
        request = Request(
            url=f'{API_ROOT}/oauth/identity',
            headers={'Authorization': f'Discogs token={token}', 'User-Agent': API_USER_AGENT, 'Accept': 'application/json'},
        )
        try:
            with urlopen(url=request, timeout=20) as response:
                identity = json.loads(response.read().decode('utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PickerError('Could not verify the Discogs token owner. No collection was selected.') from error
        owner = identity.get('username') if isinstance(identity, dict) else None
        if not isinstance(owner, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,50}', owner):
            raise PickerError('Discogs did not identify the token owner. No collection was selected.')
        identity_cache[key] = (time.monotonic() + COLLECTION_CACHE_SECONDS, owner)
    if username.casefold() != owner.casefold():
        raise PickerError(f'This token belongs to {owner}. Select that username to pick only your owned collection.')
    return owner


def owned_collection_release(username: str, token: str, release_id: Any) -> dict[str, Any] | None:
    """Verify a live collection instance, never public catalogue or wantlist membership."""
    identifier = str(release_id or '')
    if not identifier.isdigit():
        return None
    request = Request(
        url=f'{API_ROOT}/users/{quote(username, safe="")}/collection/releases/{identifier}',
        headers={
            'Authorization': f'Discogs token={token}',
            'User-Agent': API_USER_AGENT,
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
        },
    )
    try:
        with urlopen(url=request, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        if error.code == 404:
            return None
        raise PickerError(f'Could not verify collection ownership (Discogs HTTP {error.code}). Try again later.') from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PickerError('Could not verify collection ownership. No release was selected; try again.') from error
    if not isinstance(data, dict) or not isinstance(data.get('releases'), list):
        raise PickerError('Discogs returned an invalid ownership response. No release was selected.')
    instances = [
        release
        for release in data['releases']
        if isinstance(release, dict)
        and isinstance(release.get('instance_id'), int)
        and release['instance_id'] > 0
        and isinstance(release.get('basic_information'), dict)
        and str(release['basic_information'].get('id')) == identifier
    ]
    releases = collection_releases(page_data={'releases': instances})
    return releases[0] if releases else None


def random_collection_release(
    username: str,
    token: str,
    media_types: set[str],
    page_reader: Callable[[str, str, int], dict[str, Any]] = get_api_page,
    rng: ModuleType = random,
    ownership_reader: Callable[[str, str, Any], dict[str, Any] | None] = owned_collection_release,
) -> dict[str, Any]:
    if not media_types or not media_types.issubset(SUPPORTED_MEDIA_TYPES):
        raise PickerError('Choose at least one supported media type.')
    if 'vinyl' in media_types:
        media_types = media_types | {'lp'}
    candidates = load_collection(username=username, token=token, page_reader=page_reader)
    for _attempt in range(3):
        matching = [release for release in candidates if set(release['media_types']) & media_types]
        if not matching:
            raise PickerError('No currently owned releases match the selected media types.')
        candidate = rng.choice(matching)
        verified = ownership_reader(username, token, candidate['release_id'])
        if verified is not None and set(verified['media_types']) & media_types:
            selected = verified.copy()
            break
        # an unchanged collection count does not prove that cached editions are still owned.
        collection_cache.pop(username, None)
        candidates = load_collection(username=username, token=token, page_reader=page_reader)
    else:
        raise PickerError('Collection membership changed during selection. Refresh the collection and try again.')
    selected['collection_owner'] = username
    selected['ownership_verified'] = True
    if not selected.get('image') and selected.get('master_id'):
        selected['image'] = master_cover_image(master_id=selected['master_id'], token=token)
    details = catalog_details(resource='releases', identifier=selected.get('release_id'), token=token) or {}
    tracks = details.get('tracklist')
    selected['tracklist'] = [track for track in tracks if isinstance(track, dict)] if isinstance(tracks, list) else None
    selected['year'] = details.get('year') or selected.get('year')
    selected['released'] = str(details.get('released') or '')
    selected['country'] = str(details.get('country') or '')
    for field in ('genres', 'styles'):
        values = details.get(field)
        selected[field] = [value.strip() for value in values if isinstance(value, str) and value.strip()] if isinstance(values, list) else []
    labels = details.get('labels')
    selected['labels'] = (
        list(
            dict.fromkeys(
                label['name'].strip() for label in labels if isinstance(label, dict) and isinstance(label.get('name'), str) and label['name'].strip()
            )
        )
        if isinstance(labels, list)
        else []
    )
    selected['artist_background'] = artist_background(artist_id=selected.get('artist_id'), token=token)
    return selected


class PickerHandler(BaseHTTPRequestHandler):
    server_version = 'DiscogsAlbumPicker/1.0'

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == '/api/config':
            self.send_json(
                status=200,
                payload={
                    'username': DISCOGS_USERNAME,
                    'token_configured': bool(DISCOGS_PAT),
                    'token_source': DISCOGS_PAT_SOURCE,
                },
            )
            return
        if path not in ('/', '/index.html'):
            self.send_error(404)
            return
        try:
            page = (APP_DIR / 'index.html').read_bytes()
        except OSError:
            self.send_error(500, 'The app page could not be read.')
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(page)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path not in ('/api/pick', '/api/collection'):
            self.send_error(404)
            return
        origin = self.headers.get('Origin')
        server = cast(ThreadingHTTPServer, self.server)
        expected_origin = f'http://127.0.0.1:{server.server_port}'
        if origin is not None and origin != expected_origin:
            self.send_json(status=403, payload={'error': 'Requests must come from this local app.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > MAX_REQUEST_BYTES:
                raise PickerError('The request body is missing or too large.')
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            if not isinstance(payload, dict):
                raise PickerError('The request was not valid.')
            username = str(payload.get('username') or DISCOGS_USERNAME).strip()
            token = DISCOGS_PAT or str(payload.get('token', ''))
            username = authenticated_collection_user(username=username, token=token)
            if path == '/api/collection':
                self.send_json(status=200, payload=collection_inventory(username=username, token=token))
                return
            requested_media_types = payload.get('media_types')
            if not isinstance(requested_media_types, list) or not all(isinstance(media_type, str) for media_type in requested_media_types):
                raise PickerError('Choose at least one supported media type.')
            album = random_collection_release(
                username=username,
                token=token,
                media_types=set(requested_media_types),
            )
            self.send_json(status=200, payload={'album': album})
        except PickerError as error:
            self.send_json(status=400, payload={'error': str(error)})
        except UnicodeDecodeError, json.JSONDecodeError:
            self.send_json(status=400, payload={'error': 'The request was not valid JSON.'})
        except Exception:  # noqa: BLE001
            self.send_json(status=500, payload={'error': 'The picker hit an unexpected error.'})

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep the base class's parameter name for keyword-compatible overrides."""
        print(f'{self.log_date_time_string()} {self.address_string()} {format % args}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the local Discogs album picker.')
    parser.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    server = ThreadingHTTPServer(server_address=('127.0.0.1', args.port), RequestHandlerClass=PickerHandler)
    print(f'Discogs Album Picker: http://127.0.0.1:{args.port}/')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping Discogs Album Picker.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
