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
