#!/usr/bin/env python

"""
Local QA preview of the site as GitHub Pages will serve it.

Why not `mkdocs serve`?
  `mkdocs serve` is great for authoring (live rebuild + browser
  auto-reload), but it is NOT faithful to what gets deployed:
    - It serves from an in-memory build, not the real `docs/` output.
    - It skips `pydmt` and the `../data/` copy step, so pydmt-generated
      files (e.g. keys.js) and the media tracker / chess data are
      missing or stale.
    - It injects a livereload script and can handle routing /
      trailing-slashes slightly differently than a plain static server.

For QA we want the closest local approximation to GitHub Pages:
  1. Run the full build (`scripts/build_docs.sh`) to produce `docs/`
     exactly as it will be deployed.
  2. Serve `docs/` with a dumb static server.

By default this script just builds and serves; it does not open a
browser. Use --preview to launch a browser pointed at the local URL,
and --anonymous to launch that browser against a fresh temp profile
(so it is a brand-new browser process, not a tab handed off to your
running browser).
"""

import argparse
import http.server
import os
import shutil
import signal
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

DEFAULT_PORT = 8000
REPO_ROOT = Path(__file__).resolve().parent.parent


def read_site_dir():
    # Parse `site_dir:` out of mkdocs.yml without pulling in PyYAML.
    config = REPO_ROOT / "mkdocs.yml"
    for line in config.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("site_dir:"):
            value = stripped.split(":", 1)[1].strip()
            return (REPO_ROOT / value.strip("\"'")).resolve()
    return (REPO_ROOT / "_site").resolve()


def build_docs():
    subprocess.run([str(REPO_ROOT / "scripts" / "build_docs.sh")], check=True)


def start_server(port, docs_dir):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(docs_dir), **kw
    )

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def wait_for_server(url, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def find_browser():
    for name in ("google-chrome", "chromium", "chromium-browser", "firefox"):
        path = shutil.which(name)
        if path:
            return name, path
    return None, None


def launch_browser(url, anonymous):
    name, path = find_browser()
    if not path:
        print(
            "No supported browser (chrome/chromium/firefox) found in PATH.",
            file=sys.stderr,
        )
        return None, None

    profile_dir = None
    if anonymous:
        profile_dir = tempfile.mkdtemp(prefix="serve-py-profile-")
        if name == "firefox":
            args = [path, "--new-instance", "--profile", profile_dir, url]
        else:
            args = [path, f"--user-data-dir={profile_dir}", "--new-window", url]
    else:
        args = [path, url]

    proc = subprocess.Popen(args)
    return proc, profile_dir


def main():
    parser = argparse.ArgumentParser(
        description="Build the site and serve docs/ locally.",
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"port to serve on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="open a browser pointing at the local URL (default: off)",
    )
    parser.add_argument(
        "--anonymous", action="store_true",
        help="launch the preview browser with a fresh temp profile "
             "(implies --preview; default: off)",
    )
    parser.add_argument(
        "--no-build", action="store_true",
        help="skip running scripts/build_docs.sh before serving",
    )
    args = parser.parse_args()

    if args.anonymous:
        args.preview = True

    if not args.no_build:
        build_docs()

    docs_dir = read_site_dir()
    if not docs_dir.is_dir():
        print(f"site directory not found at {docs_dir}", file=sys.stderr)
        return 1

    url = f"http://127.0.0.1:{args.port}/"
    httpd = start_server(args.port, docs_dir)
    print(f"Serving {docs_dir} at {url}")

    browser_proc = None
    profile_dir = None
    try:
        if args.preview:
            if not wait_for_server(url):
                print("Server did not become ready in time.", file=sys.stderr)
                return 1
            browser_proc, profile_dir = launch_browser(url, args.anonymous)
            if args.anonymous and browser_proc is not None:
                # Anonymous launch keeps the browser process attached to this
                # temp profile, so waiting on it gives a clean shutdown signal.
                browser_proc.wait()
                return 0

        # No --preview, or --preview without --anonymous: just block until
        # the user stops the server (Ctrl-C).
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        httpd.server_close()
        if profile_dir and os.path.isdir(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
