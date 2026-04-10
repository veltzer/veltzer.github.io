# Image Management

All media cover images are stored in `blog/images/` and copied to
`docs/images/` by MkDocs during build.

## Naming Conventions

| Media Type | Pattern | Source |
|---|---|---|
| Movies | `movie-{imdb_id}.jpg` | TMDB CDN (by IMDB ID) |
| TV Series | `series-{imdb_id}.jpg` | TMDB CDN (by IMDB ID) |
| Audible | `audible-{asin}.jpg` | `cover_url` from YAML |
| Audio Courses (GC) | `audiocourse-gc-{gc_id}.jpg` | Great Courses CDN |
| Audio Courses (Audible) | `audiocourse-audible-{asin}.jpg` | Audible |
| Audio Courses (other) | `audiocourse-internal-{id}.jpg` | DuckDuckGo search |
| Museums | `museum-{internal_id}.jpg` | DuckDuckGo search |
| Podcasts | `podcast-{internal_id}.jpg` | DuckDuckGo search |
| YouTube | N/A (external) | `i.ytimg.com` at runtime |

## Adding Images for New Entries

1. Add the entry to the YAML in `../data/`
2. Run `scripts/copy_data.sh` to update `blog/data/`
3. Run the appropriate fetch script (see `doc/SCRIPTS.md`)
4. Run `scripts/check_images.py` to verify all images are present
5. Run `scripts/build_docs.sh` to build the site

## Uniform Display

All card images use `height: 200px; object-fit: cover` (in `media.css`)
to maintain consistent card heights regardless of original image dimensions.

## Caches

- TMDB/OMDB poster scripts: no cache (fast CDN downloads)
- DuckDuckGo image picker: cached in `/tmp/image_picker_cache/` per course name
- Great Courses ID lookup: cached in `/tmp/great_courses_cache.json`

Delete these to force fresh searches.

## Alternatives to Storing Images in Git

As the number of images grows, storing them directly in the Git repo
increases clone size and slows operations. Several alternatives exist:

### Git LFS (Large File Storage)

- Images stay in the normal Git workflow but are stored on a separate server.
- Setup: `git lfs install && git lfs track "*.png" "*.jpg" "*.webp"`
- GitHub free tier: 1 GB storage + 1 GB/month bandwidth; paid plans available.
- Lowest friction — no workflow changes beyond initial setup.

### External Object Storage (S3, GCS, Cloudflare R2)

- Store images in a bucket; reference them by URL in HTML/Markdown.
- Cloudflare R2 is notable for zero egress fees.
- Can place a CDN (CloudFront, Cloudflare) in front for caching and custom domains.
- Best control and scalability.

### GitHub Releases / Artifacts

- Upload images as release assets and reference via
  `https://github.com/…/releases/download/…` URLs.
- Free with no bandwidth limits for public repos.
- Good for infrequently changing assets.

### Dedicated Image Hosting (Cloudinary, imgix)

- Free tiers available; automatic resizing, format conversion (WebP/AVIF),
  and responsive image support.
- Useful when image optimization is also a goal.

### Separate Data Repository (current pattern for YAML/PGN)

- Keep images in a dedicated repo or storage location outside this repo.
- Copy them in at build time via `scripts/build_docs.sh`, similar to how
  `../data/` YAML files are handled today.
- Keeps this repo lightweight while preserving the current build workflow.

### GitHub Pages Artifact Deployment

- Use GitHub Actions to build the site and deploy via `actions/deploy-pages`.
- Images live in separate storage and are fetched during the CI build.
- The published site includes images but the source repo stays small.

### Git Submodule or Subtree for Images

- Keep images in a separate repo, reference it as a Git submodule.
- Contributors clone without images by default (`--no-recurse-submodules`).
- Similar to the `../data/` pattern but formalized within Git.

### .gitignore Images + Download Script

- Gitignore all images; add a `scripts/fetch_images.sh` that downloads them
  from their original sources (TMDB, DuckDuckGo, etc.).
- The existing fetch scripts already do this — make them the canonical source
  instead of the repo.
- Images become reproducible build artifacts rather than stored blobs.

### Lazy-Load from Original CDNs at Runtime

- For movies/TV the TMDB CDN URLs are available; YouTube already uses
  `i.ytimg.com` at runtime.
- Extend this pattern to all media types — never store images locally.
- Trade-off: depends on external CDN uptime; some sources may block hotlinking.

### Self-Hosted Image Proxy (imgproxy, thumbor)

- Run a small service that fetches, caches, and resizes images on the fly.
- Single URL pattern for all images regardless of original source.
- Can be deployed on a free tier (Fly.io, Railway).

### GitHub Issue/Comment Image Hosting

- Paste images into a GitHub issue or comment to get a
  `user-images.githubusercontent.com` URL.
- Free, no bandwidth limits, no repo bloat.
- Informal but surprisingly durable for public repos.

### WebP/AVIF Conversion in CI

- Even if images remain in the repo, convert them to modern formats during build.
- Can reduce image sizes by 50–80%, significantly lessening the Git storage impact.
- Tools: `cwebp`, `avifenc`, or `sharp` (Node.js).
