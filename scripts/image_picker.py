"""
Shared image search and picker GUI for fetching cover images.

Provides DuckDuckGo image search and a tkinter browser for selecting images.
"""

import json
import os
import re
import shutil
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageTk

SEARCH_CACHE_DIR = "/tmp/image_picker_cache"


def download(url, dest):
    """Download a URL to a file."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=15) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


def fetch_image_urls(query, max_results=20):
    """Fetch image URLs via DuckDuckGo image search API."""
    encoded = urllib.parse.quote_plus(query)
    ua = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"

    url1 = f"https://duckduckgo.com/?q={encoded}"
    req1 = urllib.request.Request(url1)
    req1.add_header("User-Agent", ua)
    try:
        with urllib.request.urlopen(req1, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            cookies = resp.headers.get_all("Set-Cookie") or []
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  DuckDuckGo search failed: {e}")
        return []

    vqd_match = re.search(r'vqd="([^"]+)"', html) or re.search(r"vqd=([a-zA-Z0-9_-]+)", html)
    if not vqd_match:
        print("  Could not get DuckDuckGo search token.")
        return []

    vqd = vqd_match.group(1)
    url2 = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={encoded}&vqd={vqd}&iaf=size:Medium"
    req2 = urllib.request.Request(url2)
    req2.add_header("User-Agent", ua)
    req2.add_header("Referer", "https://duckduckgo.com/")
    req2.add_header("Accept", "application/json")
    if cookies:
        cookie_str = "; ".join(c.split(";")[0] for c in cookies)
        req2.add_header("Cookie", cookie_str)
    try:
        with urllib.request.urlopen(req2, timeout=15) as resp:
            data = json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  DuckDuckGo image API failed: {e}")
        return []

    results = data.get("results", [])
    return [r["image"] for r in results[:max_results] if r.get("image")]


def download_candidates(query, cache_key, max_results=20):
    """Download candidate images with caching. Returns list of file paths."""
    safe_key = re.sub(r"[^\w-]", "_", cache_key)
    cache_dir = os.path.join(SEARCH_CACHE_DIR, safe_key)

    if os.path.isdir(cache_dir):
        cached = sorted(
            os.path.join(cache_dir, f) for f in os.listdir(cache_dir)
            if f.endswith(".jpg") and os.path.getsize(os.path.join(cache_dir, f)) > 1000
        )
        if cached:
            return cached

    os.makedirs(cache_dir, exist_ok=True)
    urls = fetch_image_urls(query, max_results=max_results)
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


def _build_browser_ui(root, title, info_lines):
    """Build the image browser UI layout."""
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

    info_frame = tk.Frame(root, padx=10, pady=5)
    info_frame.pack(side=tk.TOP, fill=tk.X)
    tk.Label(info_frame, text=title, font=("sans-serif", 14, "bold"), anchor="w").pack(fill=tk.X)
    for line in info_lines:
        tk.Label(info_frame, text=line, font=("sans-serif", 10), anchor="w").pack(fill=tk.X)

    img_frame = tk.Frame(root, bg="#f0f0f0")
    img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    img_label = tk.Label(img_frame, bg="#f0f0f0")
    img_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return img_label, counter_label, prev_btn, next_btn, select_btn, skip_btn, quit_btn


def show_image_browser(title, info_lines, candidates):
    """Show one large image at a time. Returns selected path, None (skip), or 'quit'."""
    result: dict[str, str | None] = {"selected": None}
    state = {"index": 0}
    img_size = 400

    root = tk.Tk()
    root.title(title)
    root.geometry("600x650")
    root.resizable(False, False)

    img_label, counter_label, prev_btn, next_btn, select_btn, skip_btn, quit_btn = \
        _build_browser_ui(root, title, info_lines)

    tk_images: list = []

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
    root.protocol("WM_DELETE_WINDOW", lambda: (result.update(selected="quit"), root.destroy()))

    import signal  # pylint: disable=import-outside-toplevel
    signal.signal(signal.SIGINT, lambda *_: (result.update(selected="quit"), root.destroy()))

    show_current()
    root.mainloop()
    return result["selected"]


def pick_image(title, info_lines, search_query, cache_key, dest_path):
    """Full flow: search, download candidates, show picker, save. Returns 'found'/'skip'/'quit'."""
    print(f"  Searching images for: {title}")
    candidates = download_candidates(search_query, cache_key)
    if not candidates:
        print("  No images found.")
        return "skip"
    print(f"  Found {len(candidates)} candidates...")
    selected = show_image_browser(title, info_lines, candidates)
    if selected == "quit":
        return "quit"
    if selected is None:
        print("  No image selected.")
        return "skip"
    shutil.copy2(selected, dest_path)
    print(f"  Saved: {dest_path}")
    return "found"
