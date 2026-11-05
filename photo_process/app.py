#!/usr/bin/env python3
"""Serve Photo Process locally and save its generated JPEGs beside the HTML."""

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, quote, unquote, urlsplit

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / 'output'
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def valid_filename(filename: str) -> bool:
    return bool(
        filename
        and filename.lower().endswith('.jpg')
        and len(filename.encode('utf-8')) <= 240
        and not re.search(r'[\x00-\x1f\x7f/\\:*?"<>|]', filename)
    )


def save_output(filename: str, data: bytes) -> str:
    """Save a generated JPEG without replacing existing photos or following links."""
    if not valid_filename(filename=filename):
        raise ValueError('The output filename is not valid.')
    if not 4 <= len(data) <= MAX_IMAGE_BYTES or not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
        raise ValueError('The output must be a JPEG smaller than 10 MB.')
    if OUTPUT_DIR.is_symlink():
        raise ValueError('The output directory must not be a symbolic link.')
    OUTPUT_DIR.mkdir(exist_ok=True)
    # exclusive creation preserves earlier outputs, even for simultaneous requests.
    for number in range(1, 10001):
        name = filename if number == 1 else f'{Path(filename).stem}-{number}.jpg'
        try:
            with (OUTPUT_DIR / name).open(mode='xb') as output:
                output.write(data)
            return name
        except FileExistsError:
            continue
    raise ValueError('Too many files already use this output name.')


class PhotoHandler(BaseHTTPRequestHandler):
    server_version = 'PhotoProcess/1.0'

    def send_body(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        self.send_body(status=status, content_type='application/json; charset=utf-8', body=json.dumps(payload).encode('utf-8'))

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == '/api/config':
            self.send_json(status=200, payload={'save_output': True, 'output_directory': './output/'})
            return
        if path in ('/', '/photo_process.html'):
            target = APP_DIR / 'photo_process.html'
            content_type = 'text/html; charset=utf-8'
        elif path.startswith('/output/'):
            filename = unquote(path[len('/output/') :])
            if not valid_filename(filename=filename) or OUTPUT_DIR.is_symlink():
                self.send_error(404)
                return
            target = OUTPUT_DIR / filename
            if target.is_symlink():
                self.send_error(404)
                return
            content_type = 'image/jpeg'
        else:
            self.send_error(404)
            return
        try:
            data = target.read_bytes()
        except OSError:
            self.send_error(404)
            return
        self.send_body(status=200, content_type=content_type, body=data)

    def do_POST(self) -> None:
        request = urlsplit(self.path)
        if request.path != '/api/output':
            self.send_error(404)
            return
        server = cast(ThreadingHTTPServer, self.server)
        # an unrelated website must not be able to write to the local output folder.
        if self.headers.get('Origin') != f'http://127.0.0.1:{server.server_port}':
            self.send_json(status=403, payload={'error': 'Requests must come from this local app.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 4 <= length <= MAX_IMAGE_BYTES or self.headers.get('Content-Type') != 'image/jpeg':
                raise ValueError('The output must be a JPEG smaller than 10 MB.')
            filenames = parse_qs(request.query).get('filename', [])
            if len(filenames) != 1:
                raise ValueError('Specify one output filename.')
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError('The output image was incomplete.')
            filename = save_output(filename=filenames[0], data=data)
        except ValueError as error:
            self.send_json(status=400, payload={'error': str(error)})
            return
        except OSError:
            self.send_json(status=500, payload={'error': 'Could not save the image in ./output/. Check folder access and free space.'})
            return
        self.send_json(status=201, payload={'filename': filename, 'path': f'./output/{filename}', 'url': f'/output/{quote(filename, safe="")}'})


def main() -> None:
    parser = argparse.ArgumentParser(description='serve Photo Process and save JPEGs in ./output/')
    parser.add_argument('--port', type=int, default=8770)
    args = parser.parse_args()
    server = ThreadingHTTPServer(server_address=('127.0.0.1', args.port), RequestHandlerClass=PhotoHandler)
    print(f'Photo Process: http://127.0.0.1:{args.port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
