# Analytics Options for the Blog

Since this site is a static site hosted on GitHub Pages, there is no server-side analytics. We must use client-side (JavaScript) tracking or third-party integrations.

## 1. GoatCounter (Recommended)
A privacy-first, lightweight, and open-source analytics service. It is free for personal/non-commercial use.
*   **Pros:** No cookies required (no GDPR banner needed), extremely fast, privacy-focused.
*   **Setup:**
    1.  Create an account at [GoatCounter](https://www.goatcounter.com/).
    2.  Add your tracking code to `mkdocs.yml` under `extra_javascript` or via a theme override.
*   **Theme Integration:**
    ```yaml
    extra_javascript:
      - https://gc.zgo.at/count.js
    ```

## 2. Google Analytics 4 (GA4)
The industry standard for detailed traffic analysis.
*   **Pros:** Most powerful features, built-in support in the MkDocs Material theme.
*   **Cons:** Privacy-heavy, requires cookie consent in many jurisdictions.
*   **Setup:**
    Add your measurement ID to `mkdocs.yml`:
    ```yaml
    extra:
      analytics:
        provider: google
        property: G-XXXXXXXXXX
    ```

## 3. Cloudflare Web Analytics
A privacy-focused alternative that doesn't require a Cloudflare proxy (it works via a JS snippet).
*   **Pros:** Free, no cookies, simple dashboard.
*   **Setup:**
    1.  Add the script provided by Cloudflare to `extra_javascript` in `mkdocs.yml`.

## 4. GitHub Insights (Basic)
GitHub provides a "Traffic" tab in the repository settings.
*   **Location:** `Insights -> Traffic`
*   **Limitations:** Only shows the last 14 days of data and only the top 10 most visited pages.

## Comparison Summary

| Feature | GoatCounter | Google Analytics | Cloudflare | GitHub Insights |
| :--- | :--- | :--- | :--- | :--- |
| **Privacy** | High (No cookies) | Low (Cookies) | High (No cookies) | N/A (Internal) |
| **Setup** | Easy | Very Easy | Easy | None |
| **Detail** | Moderate | High | Moderate | Very Low |
| **Cost** | Free (Personal) | Free | Free | Free |

---

# Visible On-Page Visitor Counter

**This is a different problem from the analytics options above, and the distinction is the
whole point.** Everything above is a *dashboard*: it records visits and shows them to you,
the owner. The `Page Visits:` line in `media.md` / `media_app.html` needs the opposite —
a number fetched back *into the page* and shown to the visitor.

No analytics product does the second thing. Findings below were tested on 2026-08-15 from
the real `https://veltzer.org` origin in a browser, not read off documentation.

## The blocker: CORS

`media-app.js` uses `fetch()` and writes the result into a `<span>`. That requires the
service to send an `Access-Control-Allow-Origin` header. Most free counters are **SVG
badges** built for `<img>` tags in GitHub READMEs, and they send no CORS headers at all —
so `fetch()` fails even though the same URL works fine as an image.

## Tested results

| Service | Signup | Returns JSON | Works via `fetch()` from veltzer.org |
| :--- | :--- | :--- | :--- |
| **counterapi.dev v2** | Yes | Yes | **Yes** — sends CORS headers |
| **dwyl/hits** | No | Yes | **No** — CORS blocked (`Failed to fetch`) |
| **visitor-badge.laobi.icu** | No | No (SVG) | Image only — loads 67x20 |
| **hitcounter.pythonanywhere.com** | No | No (SVG) | Image failed to load |
| **countapi.xyz** | — | — | **Dead** — no response (HTTP 000) |

Notes on the two that nearly worked:

*   **dwyl/hits** was the most promising: free, no signup, real JSON, and verified to
    increment correctly (three requests returned 1, 2, 3). It is unusable via `fetch()`
    purely because of the missing CORS headers. It *does* work as an `<img>` badge
    (verified, 80x20).
*   **counterapi.dev v2** is the only JSON option that survives CORS — a browser request
    returned a readable `404 {"code":"404","message":"Workspace not found"}` rather than a
    network error, which proves the CORS headers are present. It needs a workspace plus an
    API key sent as `Authorization: Bearer ...`. On a public static site that token is
    readable by anyone viewing source, so it is only acceptable if it can be scoped to
    increment-only — the same reasoning that makes the Calendar browser key safe to publish
    (see `doc/DECISIONS.md`). Confirm their token scoping before relying on it.

## Why Google cannot do this

GA4 is free and the MkDocs Material theme supports it natively (section 2 above), but it
splits into two halves:

*   **Writing** a visit — public, client-side, trivial. That is the `gtag` snippet.
*   **Reading** the count back — requires the **GA4 Data API**, which needs OAuth 2.0 or a
    service-account key.

That credential is a genuine secret. Unlike the referrer-restricted, read-only Calendar
browser key, a GA service-account key grants access to your analytics data and cannot be
safely restricted for public exposure — putting it in `keys.js` would hand out read access
to your traffic data. So the number cannot be fetched client-side.

The workarounds all need infrastructure this site does not have: fetch at build time (the
count is then stale until the next deploy), or a proxy / serverless function holding the
credential — which is exactly the edge-proxy complexity `doc/DECISIONS.md` already rejected
for the Calendar key.

## Recommendation

The two goals are separable, and it is worth deciding which one is actually wanted:

*   **To know the traffic** — GoatCounter (or GA4). Three lines of config, covers all 80
    blog posts and the app pages, not just the two media pages the old counter touched.
    GoatCounter is preferable here specifically because it sets no cookies and therefore
    needs no GDPR consent banner.
*   **To show a number on the page** — a badge `<img>` is the only no-signup option that
    works today. The cost is a fixed-style image rather than a number that can be styled to
    match the page.

These are not exclusive; GoatCounter for real analytics plus a badge for the visible count
is a coherent combination.

See the "Visitor Counter" entry in `doc/IMPROVEMENTS.md` for the current state of the
disabled counter and the `COUNTER_ENDPOINT` hook left in `media-app.js`.
