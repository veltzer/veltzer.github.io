#!/usr/bin/env python

"""
Fetch cover images for all audio courses.

Priority:
1. great_courses_id -> download from Great Courses CDN
   -> audiocourse-gc-{id}.jpg
2. audible_asin -> download from Audible page (og:image)
   -> audiocourse-audible-{asin}.jpg
3. Neither -> DuckDuckGo image search with GUI picker
   -> audiocourse-internal-{n}.jpg

Usage:
  scripts/fetch_audiocourse_images.py [--force]
"""

import argparse
import os
import re
import shutil
import sys
import time
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request  # pylint: disable=ungrouped-imports

from PIL import Image, ImageTk

IMAGE_DIR = "blog/images"
GC_IMAGE_URL = "https://secureimages.teach12.com/tgc/images/m2/wondrium/courses/{cid}/{cid}.jpg"
AUDIBLE_URL = "https://www.audible.com/pd/{asin}"
YAML_PATH = "../data/yaml/audio_courses.yaml"

def download(url, dest):
    """Download a URL to a file."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


def fetch_audible_image_url(asin):
    """Fetch the og:image URL from an Audible page."""
    url = AUDIBLE_URL.format(asin=asin)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  Audible fetch failed: {e}", file=sys.stderr)
        return None
    m = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    return m.group(1) if m else None


def load_entries():
    """Load course entries from YAML."""
    entries = []
    current: str | None = None
    fields: dict[str, str] = {}
    with open(YAML_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- name:"):
                if current:
                    entries.append((current, dict(fields)))
                current = s.split(":", 1)[1].strip().strip("'\"")
                fields = {}
            elif ":" in s and current:
                key, val = s.split(":", 1)
                fields[key.strip()] = val.strip().strip("'\"")
    if current:
        entries.append((current, dict(fields)))
    return entries


def get_dest_path(entry_type, entry_id):
    """Get destination file path."""
    return os.path.join(IMAGE_DIR, f"audiocourse-{entry_type}-{entry_id}.jpg")



def fetch_image_urls(name, max_results=10):
    """Fetch image URLs via DuckDuckGo image search API."""
    import json as _json  # pylint: disable=import-outside-toplevel
    query = f"{name} the great courses cover"
    encoded = urllib.parse.quote_plus(query)

    ua = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"

    # Step 1: Get vqd token and cookies
    url1 = f"https://duckduckgo.com/?q={encoded}"
    req1 = urllib.request.Request(url1)
    req1.add_header("User-Agent", ua)
    try:
        with urllib.request.urlopen(req1, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            cookies = resp.headers.get_all("Set-Cookie") or []
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  DuckDuckGo search failed: {e}", file=sys.stderr)
        return []

    vqd_match = re.search(r'vqd="([^"]+)"', html) or re.search(r"vqd=([a-zA-Z0-9_-]+)", html)
    if not vqd_match:
        print("  Could not get DuckDuckGo search token.", file=sys.stderr)
        return []

    # Step 2: Fetch image results with referer and cookies
    vqd = vqd_match.group(1)
    url2 = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={encoded}&vqd={vqd}"
    req2 = urllib.request.Request(url2)
    req2.add_header("User-Agent", ua)
    req2.add_header("Referer", "https://duckduckgo.com/")
    req2.add_header("Accept", "application/json")
    if cookies:
        cookie_str = "; ".join(c.split(";")[0] for c in cookies)
        req2.add_header("Cookie", cookie_str)
    try:
        with urllib.request.urlopen(req2, timeout=15) as resp:
            data = _json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  DuckDuckGo image API failed: {e}", file=sys.stderr)
        return []

    results = data.get("results", [])
    urls = [r["image"] for r in results[:max_results] if r.get("image")]
    return urls



SEARCH_CACHE_DIR = "/tmp/audiocourse_search_cache"


def get_cache_dir_for(name):
    """Get a persistent cache directory for a course name's search results."""
    safe_name = re.sub(r"[^\w-]", "_", name)
    return os.path.join(SEARCH_CACHE_DIR, safe_name)


def download_candidates(name, max_results=20):
    """Download candidate images, using cache if available. Returns list of file paths."""
    cache_dir = get_cache_dir_for(name)

    # Check cache first
    if os.path.isdir(cache_dir):
        cached = sorted(
            os.path.join(cache_dir, f) for f in os.listdir(cache_dir)
            if f.endswith(".jpg") and os.path.getsize(os.path.join(cache_dir, f)) > 1000
        )
        if cached:
            return cached

    # Download fresh
    os.makedirs(cache_dir, exist_ok=True)
    urls = fetch_image_urls(name, max_results=max_results)
    candidates = []
    for i, url in enumerate(urls):
        dest_path = os.path.join(cache_dir, f"candidate_{i}.jpg")
        try:
            download(url, dest_path)
            if os.path.getsize(dest_path) > 1000:
                candidates.append(dest_path)
            else:
                os.unlink(dest_path)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError):
            continue
    return candidates


def _build_browser_ui(root, name, fields):
    """Build the image browser UI layout. Returns (img_label, counter_label, prev_btn, next_btn)."""
    # Buttons at bottom (packed first so they're never hidden)
    btn_frame = tk.Frame(root, padx=10, pady=8)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

    prev_btn = tk.Button(btn_frame, text="\u25c0 Prev", font=("sans-serif", 11), padx=10, pady=5)
    prev_btn.pack(side=tk.LEFT, padx=3)
    next_btn = tk.Button(btn_frame, text="Next \u25b6", font=("sans-serif", 11), padx=10, pady=5)
    next_btn.pack(side=tk.LEFT, padx=3)
    select_btn = tk.Button(btn_frame, text="Select this", font=("sans-serif", 11, "bold"),
                           padx=15, pady=5, bg="#4CAF50", fg="white")
    select_btn.pack(side=tk.LEFT, padx=10)
    skip_btn = tk.Button(btn_frame, text="None of these", font=("sans-serif", 11), padx=10, pady=5)
    skip_btn.pack(side=tk.LEFT, padx=3)
    quit_btn = tk.Button(btn_frame, text="Quit", font=("sans-serif", 11),
                         padx=10, pady=5, fg="red")
    quit_btn.pack(side=tk.RIGHT, padx=3)

    counter_label = tk.Label(root, font=("sans-serif", 11))
    counter_label.pack(side=tk.BOTTOM, pady=2)

    # Info at top
    info_frame = tk.Frame(root, padx=10, pady=5)
    info_frame.pack(side=tk.TOP, fill=tk.X)
    tk.Label(info_frame, text=name, font=("sans-serif", 14, "bold"), anchor="w").pack(fill=tk.X)
    for field in ("lecturers", "rating", "review", "device", "location", "progress"):
        if field in fields:
            tk.Label(info_frame, text=f"{field}: {fields[field]}",
                     font=("sans-serif", 10), anchor="w").pack(fill=tk.X)

    # Image area
    img_frame = tk.Frame(root, bg="#f0f0f0")
    img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    img_label = tk.Label(img_frame, bg="#f0f0f0")
    img_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return img_label, counter_label, prev_btn, next_btn, select_btn, skip_btn, quit_btn


def show_image_browser(name, fields, candidates):
    """Show one large image at a time with prev/next/select/skip/quit. Returns path or None/'quit'."""
    result: dict[str, str | None] = {"selected": None}
    state = {"index": 0}
    img_size = 400

    root = tk.Tk()
    root.title(f"Pick image for: {name}")
    root.geometry("600x650")
    root.resizable(False, False)

    img_label, counter_label, prev_btn, next_btn, select_btn, skip_btn, quit_btn = \
        _build_browser_ui(root, name, fields)

    tk_images = []  # prevent GC

    def show_current():
        idx = state["index"]
        try:
            img = Image.open(candidates[idx])
            img.thumbnail((img_size, img_size))
            tk_img = ImageTk.PhotoImage(img)
            tk_images.clear()
            tk_images.append(tk_img)
            img_label.config(image=tk_img, text="")
        except (OSError, ValueError):
            img_label.config(image="", text="(failed to load)")
        counter_label.config(text=f"Image {idx + 1} of {len(candidates)}")
        prev_btn.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        next_btn.config(state=tk.NORMAL if idx < len(candidates) - 1 else tk.DISABLED)

    def on_prev():
        if state["index"] > 0:
            state["index"] -= 1
            show_current()

    def on_next():
        if state["index"] < len(candidates) - 1:
            state["index"] += 1
            show_current()

    prev_btn.config(command=on_prev)
    next_btn.config(command=on_next)
    select_btn.config(command=lambda: (result.update(selected=candidates[state["index"]]), root.destroy()))
    skip_btn.config(command=root.destroy)
    quit_btn.config(command=lambda: (result.update(selected="quit"), root.destroy()))

    root.bind("<Left>", lambda _: on_prev())
    root.bind("<Right>", lambda _: on_next())
    root.bind("<Return>", lambda _: select_btn.invoke())
    root.bind("<Escape>", lambda _: skip_btn.invoke())
    root.bind("q", lambda _: quit_btn.invoke())

    show_current()
    root.mainloop()
    return result["selected"]


def handle_image_search(name, fields, force):
    """Search for images and show browser picker."""
    internal_id = fields.get("internal_id")
    if not internal_id:
        print(f"  WARNING: {name} has no internal_id, skipping.")
        return "skip"

    dest = get_dest_path("internal", internal_id)
    if os.path.exists(dest) and not force:
        return "skip"

    print(f"\n  No external ID for: {name} (internal_id: {internal_id})")
    for field in ("lecturers", "rating", "review", "device", "location", "progress"):
        if field in fields:
            print(f"    {field + ':':11s} {fields[field]}")

    print("  Searching DuckDuckGo Images...")
    candidates = download_candidates(name, max_results=20)

    if not candidates:
        print("  No images found.")
        return "skip"

    print(f"  Found {len(candidates)} candidates, showing browser...")
    selected = show_image_browser(name, fields, candidates)

    if selected == "quit":
        return "quit"
    if selected is None:
        print("  No image selected.")
        return "skip"

    shutil.copy2(selected, dest)
    print(f"  Saved: {dest}")
    return "found"


def fetch_gc_image(name, gc_id, force):
    """Download image from Great Courses CDN. Returns 'downloaded', 'skipped', or 'failed'."""
    dest = get_dest_path("gc", gc_id)
    if os.path.exists(dest) and not force:
        return "skipped"
    url = GC_IMAGE_URL.format(cid=gc_id)
    try:
        download(url, dest)
        print(f"  Downloaded (GC): {name} -> {dest}")
        return "downloaded"
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  Failed (GC) {name}: {e}", file=sys.stderr)
        return "failed"


def fetch_audible_image(name, asin, force):
    """Download image from Audible. Returns 'downloaded', 'skipped', or 'failed'."""
    dest = get_dest_path("audible", asin)
    if os.path.exists(dest) and not force:
        return "skipped"
    image_url = fetch_audible_image_url(asin)
    if not image_url:
        print(f"  No image found on Audible for: {name}")
        return "failed"
    try:
        download(image_url, dest)
        print(f"  Downloaded (Audible): {name} -> {dest}")
        return "downloaded"
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  Failed (Audible) {name}: {e}", file=sys.stderr)
        return "failed"


def process_entry(name, fields, force):
    """Process one entry. Returns 'downloaded', 'skipped', 'failed', or 'quit'."""
    gc_id = fields.get("great_courses_id")
    asin = fields.get("audible_asin")
    if gc_id:
        result = fetch_gc_image(name, gc_id, force)
        time.sleep(0.2)
        return result
    if asin:
        result = fetch_audible_image(name, asin, force)
        time.sleep(0.3)
        return result
    return handle_image_search(name, fields, force)


def main():
    parser = argparse.ArgumentParser(description="Fetch audio course cover images")
    parser.add_argument("--force", action="store_true", help="Re-download existing images")
    args = parser.parse_args()

    os.makedirs(IMAGE_DIR, exist_ok=True)
    entries = load_entries()
    downloaded = 0
    skipped = 0
    failed = 0

    print(f"Found {len(entries)} courses\n")

    for name, fields in entries:
        status = process_entry(name, fields, args.force)
        if status == "downloaded":
            downloaded += 1
        elif status == "quit":
            print("Quitting.")
            break
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
