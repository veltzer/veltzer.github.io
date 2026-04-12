#!/bin/bash -eu

# Local QA preview of the site as GitHub Pages will serve it.
#
# Why not `mkdocs serve`?
#   `mkdocs serve` is great for authoring (live rebuild + browser
#   auto-reload), but it is NOT faithful to what gets deployed:
#     - It serves from an in-memory build, not the real `docs/` output.
#     - It skips `pydmt` and the `../data/` copy step, so pydmt-generated
#       files (e.g. keys.js) and the media tracker / chess data are
#       missing or stale.
#     - It injects a livereload script and can handle routing /
#       trailing-slashes slightly differently than a plain static server.
#
# For QA we want the closest local approximation to GitHub Pages:
#   1. Run the full build (`scripts/build_docs.sh`) to produce `docs/`
#      exactly as it will be deployed.
#   2. Serve `docs/` with a dumb static server (`python3 -m http.server`).
#
# The script also opens a dedicated browser window against a temp
# profile. A temp profile guarantees a fresh browser process (rather
# than handing the URL off to an already-running browser and returning
# immediately), so `wait` can block on it. When that window is closed,
# the EXIT trap tears down the static server and removes the profile.

URL="http://127.0.0.1:8000/"
PORT=8000
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Full production-like build.
"${REPO_ROOT}/scripts/build_docs.sh"

# 2. Serve the built `docs/` directory statically.
python3 -m http.server -d "${REPO_ROOT}/docs" "${PORT}" &
SERVER_PID=$!

PROFILE_DIR=$(mktemp -d)

cleanup() {
    if kill -0 "${SERVER_PID}" 2>/dev/null; then
        kill "${SERVER_PID}" 2>/dev/null || true
        wait "${SERVER_PID}" 2>/dev/null || true
    fi
    rm -rf "${PROFILE_DIR}"
}
trap cleanup EXIT INT TERM

# Wait for the server to start accepting connections.
for _ in $(seq 1 50); do
    if curl -s -o /dev/null "${URL}"; then
        break
    fi
    sleep 0.2
done

if command -v google-chrome >/dev/null 2>&1; then
    BROWSER=google-chrome
elif command -v chromium >/dev/null 2>&1; then
    BROWSER=chromium
elif command -v chromium-browser >/dev/null 2>&1; then
    BROWSER=chromium-browser
elif command -v firefox >/dev/null 2>&1; then
    BROWSER=firefox
else
    echo "No supported browser (chrome/chromium/firefox) found in PATH." >&2
    exit 1
fi

case "${BROWSER}" in
    firefox)
        "${BROWSER}" --new-instance --profile "${PROFILE_DIR}" "${URL}"
        ;;
    *)
        "${BROWSER}" --user-data-dir="${PROFILE_DIR}" --new-window "${URL}"
        ;;
esac
