# Search Console and Indexing

The state of the site as Google sees it: what was wrong, what was fixed, what
is deliberately left alone, and what is still open. Written 2026-09-07 against
the `veltzer.org` domain property.

Search Console is at
<https://search.google.com/search-console?resource_id=sc-domain:veltzer.org>.

## The two issues that were fixed

Search Console raised two messages on 2026-09-07, both under Page indexing:

- *New reasons prevent pages from being indexed on site veltzer.org* --
  Not found (404), Page with redirect, Excluded by 'noindex' tag.
- *New reasons prevent pages in a sitemap from being indexed on site
  veltzer.org* -- Page with redirect.

Both trace to the same history: the MkDocs-to-zola migration, and English
content later moving under `/en/`. They are
separate problems with separate fixes, and the second is the more consequential
of the two.

### Not found (404) -- 9 pages

Every one was a live page at a changed URL, not missing content. Two
generations of stale URL were represented:

- MkDocs-era permalinks, `/YYYY/MM/DD/<slug>/`. The slug came from the post
  *title*, so a later retitling stranded the old URL even where the post never
  moved. This is why `divine_command_theory_problems` was being requested as
  `/2026/05/13/what-divine-command-theory-actually-implies/`, and
  `brain_damage_disproves_the_soul` as
  `/2026/05/18/what-brain-damage-tells-us-about-the-soul/`. The dates in those
  two URLs do not even match the posts' current front matter.
- Root-level zola URLs from before English moved to `/en/` --
  `/calendar/`, `/blog/algo-trading-short-timescales/`, `/page/5/`. These
  differ from the live URL by exactly one path segment.

Plus `/ascx/public_key.asc`, an address from the pre-MkDocs site still linked
from old signatures and mailing-list archives.

Fixed by `write_legacy_redirects()` in `scripts/build_site.py`, which emits a
meta-refresh stub carrying `rel=canonical` and `noindex, follow` for each. The
map is `LEGACY_REDIRECTS`; paginator URLs are expanded from the build output
rather than hand-listed, so the archive can grow without the list going stale.

**These cannot be zola `aliases`, and that was verified rather than assumed.**
An alias for a default-language page is written to the site root, and
`relocate_english()` then sweeps every root directory into `/en/` -- so the
alias is built, moved, and ends up serving `/en/blog/blog/x/` while the URL it
was meant to rescue still 404s. A build with one such alias in place confirmed
this. Hence the step runs *after* the move, in the post-processing chain.

Re-checked 2026-09-21, after every post and section became an explicit
`_index.en.md` / `.en.md` under the phantom `cs` default language: zola still
writes an English post's alias to the site root (`/2026/01/01/old-slug/`, not
`/en/...`). Later the same day `relocate_english()` was removed -- with every
section suffixed it had nothing left to move -- so an alias would now stay
where zola writes it and could serve a MkDocs-era post URL. The
post-processing step is kept anyway: aliases exist only for pages, while the
paginator URLs, `/ascx/public_key.asc` and the section URLs rescued here are
not pages, and one mechanism for every legacy URL beats two. Switching the
post URLs to aliases is possible now but has not been done.

`noindex, follow` matters: without it Google would index the stubs themselves
as thin duplicates, trading nine 404s for nine near-empty pages.

### Page with redirect, in a sitemap -- 112 URLs

This was the real defect, and it was larger than the six pages the message
named.

Zola gives every paginated section a `/page/1/` URL and builds it as a stub
that bounces to the paginator root -- `/en/tags/atheism/page/1/` redirects to
`/en/tags/atheism/`. The page is real; that URL is just not the one serving it.
Zola listed both in the sitemap. With 55 tags per language plus the two blog
indexes, that was **112 of 629 sitemap entries pointing at a redirect**.

A sitemap is a statement about canonical, indexable URLs, so an entry that
redirects contradicts it. Fixed by `drop_redirecting_urls()`, called from
`fix_sitemap()`.

Only `/page/1/` is affected. `page/2` upward are real paginated pages and are
left alone -- a filter broad enough to catch them would drop the archive tail
out of the index. The redirects themselves also stay, so anyone holding a
`/page/1/` link still lands in the right place; only the sitemap entry goes.

### Verification

Both fixes shipped in commit `09467b8`. What was actually checked, in order:

- Against the **live site before the change**: each of the 9 reported URLs
  returned 404 and each `/en/` target returned 200. The mapping is measured,
  not guessed.
- Every generated redirect resolves to a page that exists: 25 of them
  (8 one-off, plus 17 paginator pages -- `/page/5/` was the only one Google
  reported, but the whole run was equally stranded), 0 broken.
- Sitemap went from 629 entries (517 real, 112 redirecting) to **517, all
  serving real pages, 0 redirects, 0 missing, 0 duplicates**.
- Cold `rsconstruct build` after `rsconstruct clean all`: 869 built, 0 failed.
- After deploy, against the live site: all 9 URLs return 200, the live
  `sitemap.xml` has 517 entries and zero `/page/1/` URLs, and a 25-URL random
  sample of live sitemap entries returned 200 with zero redirects.

## The 2026-09-16 round: both validations failed, and why

Both validations came back **Failed** (started 9/7, failed 9/15), and Search
Console sent three messages on 2026-09-16:

- *Some fixes failed for Page indexing issues* -- the `Not found (404)`
  validation.
- *New reasons prevent pages from being indexed* -- `Duplicate without
  user-selected canonical` and `Alternate page with proper canonical tag`.
- *New reasons prevent pages in a sitemap from being indexed* -- `Alternate
  page with proper canonical tag`.

The failure was **not** a regression in the 2026-09-07 fix. Every URL that
fix named still returns 200, verified against the live site on 2026-09-22.
What happened is that the recrawl reached URLs the fix never covered, and
those are what failed the validation:

| Reported URL | State on 2026-09-22 | Cause |
| --- | --- | --- |
| 6 of the 12 reported 404s | 200 | fixed 9/7, awaiting recrawl |
| `/2026/04/18/...soul/`, `/2026/04/07/religions...`, `/2026/04/26/the-equivocation...` | 404 | MkDocs permalinks, never mapped |
| `/2010/07/21/<hebrew title>/` | 404 | the one Hebrew MkDocs permalink |
| `/blog/two-kinds-of-believers/` | 404 | root-level URL, never mapped |
| `/jschess/` | 404 | the chess viewer's first home |

A validation checks only the URLs it started with, so three MkDocs permalinks
and a Hebrew one that were never in `LEGACY_REDIRECTS` were enough to fail
the whole run.

### Duplicate without user-selected canonical -- 6 pages

All six were root-level post URLs from before English moved to `/en/`:
`/blog/engineers-pay-for-everyones-fantasies/` and five siblings. Google held
both the old root URL and the `/en/` one, neither pointed at the other, so it
picked its own canonical and dropped the rest as duplicates. The redirect stub
supplies the missing `rel=canonical`.

### Alternate page with proper canonical tag -- 1 page

`/en/calendar/`, and **this one is correct as it stands**. The page carries
`rel=canonical` to itself and `hreflang` alternates to `/he/calendar/`, which
is exactly what a bilingual page should do. Google is reporting that it chose
the Hebrew page as canonical for a query, which is the mechanism working, not
a defect. Nothing to fix; recorded so the next reader does not go changing the
canonical logic.

### `http://www.veltzer.org/` under Page with redirect

Also correct. It serves a single 301 to `https://veltzer.org/`, which is what
a non-canonical host should do. GitHub Pages handles it; no change here.

### The fix, 2026-09-22

`LEGACY_REDIRECTS` grew from 8 one-off entries to 29, covering the four new
MkDocs permalinks (three English, one Hebrew), the seven root-level post URLs,
`/jschess/`, and the nine **section roots** (`/blog/`, `/tags/`, `/about/`,
`/media/`, `/chess/`, `/slides/`, `/syllabi/`, `/animations/`, `/training/`).
The section roots were a known open item in `doc/IMPROVEMENTS.md` -- "`/blog/`
is a bare 404" -- and are fixed here because they are the same defect as the
post URLs and were about to fail the next validation the same way.

`tests/test_legacy_redirects.py` was added at the same time. The map is now
large enough that a typo would ship silently and surface as a Search Console
404 weeks later, so the invariants that hold without a build are checked:
sources relative and unslashed, targets rooted and language-prefixed, no
self-redirect, and no stub pointing at another stub (a meta-refresh chain is
a link Google may decline to follow).

Verified: cold `rsconstruct clean all` + `rsconstruct build`, 880 built,
0 failed. All **46** redirect stubs resolve to a page that exists, 0 broken,
up from 25. Sitemap: 527 URLs, no stubs listed, no `/page/1/`.

Deployed and verified live on 2026-09-22: all 12 reported 404s, all 6
duplicate-canonical URLs and all 10 section roots return 200.

Validation was then restarted for all three Website-sourced reasons, and each
reads **Started**:

| Reason | Pages | Validation |
| --- | --- | --- |
| Not found (404) | 12 | Started 9/22 |
| Page with redirect | 16 | Started 9/22 |
| Duplicate without user-selected canonical | 6 | Started 9/22 |

The `Page with redirect` run is expected to pass without any code change:
its 16 URLs are 13 `/page/1/` paginator stubs, already dropped from the
sitemap on 2026-09-07 and still correctly bouncing to the paginator root,
plus the three host variants (`http://veltzer.org/`, `http://www.veltzer.org/`,
`https://www.veltzer.org/`), each serving a single 301 to the canonical host.
It failed on 9/15 only because Google re-checks the URL rather than the
sitemap entry. Nothing there is broken.

`Alternate page with proper canonical tag` was deliberately **not**
validated: its one page is `/en/calendar/`, which is correct as it stands
(see above), so there is no fix to validate.

## Open: 190 "Discovered - currently not indexed"

The largest not-indexed bucket by far -- 190 of 218 -- and **untouched by the
work above**, deliberately.

Search Console attributes it to *Google systems*, not *Website*. Google found
the URLs and chose not to spend crawl budget on them. There is no broken thing
in the build to fix; it is a content, internal-linking and site-authority
question, and it deserves real investigation rather than a guess at a cause.
The 9 "Crawled - currently not indexed" are the same category, smaller.

This is the obvious next piece of SEO work on this site, and it is genuinely
open.

One caveat before anyone investigates: this is a **domain** property, so it
covers every repo publishing to `veltzer.org`, not just this site. The indexed
count (807) is well above this site's sitemap (517 URLs), and other repos'
generated docs -- `pyscrapers`, `pytconf` -- appear in the indexed list. So the
190 are not known to be this site's pages, and the first step is to find out
whose they are before treating them as a defect here.

## Deliberately not fixed: Excluded by 'noindex' -- 4 pages

`/rsdedup/print.html`, `/rsdedup/toc.html`, `/rscalendar/print.html`,
`/rscalendar/toc.html`. These are **mdBook** output, not built by this repo:
`rsdedup` and `rscalendar` each keep an mdBook under `docs/` (`docs/book.toml`,
`build-dir = "book"`) and publish it to a path on this domain. mdBook emits
`print.html` (the whole book on one printable page) and `toc.html` alongside
the real chapters, and stamps both with `<meta name="robots" content="noindex">`
itself. Confirmed by fetching all four URLs.

They are correct as they are. Both are duplicate renderings of chapter content
that is already indexed at its own URL, so the `noindex` is doing its job --
removing it would put four duplicates into the index competing with the real
pages.

Search Console reports these as a *reason pages are not indexed*, which reads
like a defect and is not one. Recorded here so the next person to read that
report does not go fixing them -- and note that the fix would not live in this
repo anyway, but in the `rsdedup` and `rscalendar` repositories.

**Expect this count to grow, and do not read that as a regression.** All 21
`rs*` repos publish an mdBook the same way -- byte-identical `docs/book.toml`
and a byte-identical `docs:` job in `.github/workflows/ci.yml` -- so 42 such
pages exist on the domain, all carrying the same `noindex`. Only 4 are
reported because Search Console lists pages it has actually crawled, and it
had reached these two books by 2026-08-26. As it works through the rest the
figure drifts toward 42. `rsdedup` and `rscalendar` are not special; they were
simply crawled first.

## Declined: listing the rs* books in this site's sitemap

The 21 `rs*` mdBooks are in no sitemap at all -- no `rs*` URL appears in this
site's `sitemap.xml`, none of the books ships its own
(`/rsdedup/sitemap.xml` is a 404), and nothing on this site links to them.
Google reaches them only by following each repo's GitHub `homepage` field
inward, which is why crawl coverage is so uneven.

**Considered and declined for this repo.** The books are not part of this site.
Zola generates the sitemap from what it built out of `content/`, `templates/`
and `static/`; the books are built by 21 other repositories' workflows and
deployed to `veltzer.org/<repo>/` independently. Nothing in this build knows
those paths exist, so covering them would mean hand-injecting a list of 21 repo
names into `fix_sitemap()` -- a hand-maintained parallel list that cannot
verify a repo still exists or which chapters it now has. `doc/IMPROVEMENTS.md`
records deleting exactly that shape of thing once already (the old
`blog/sitemap.xml`, stale and listing URLs that no longer existed).

If it is ever worth fixing, it belongs in the `rs*` repos' shared `docs:` job
or their `book.toml`, not here. Note two constraints there: that workflow is a
byte-identical fleet invariant, so it changes in all 21 at once or not at all;
and the job only runs on a release commit, so a change would reach each book's
site only when that repo next cuts a release.

This site's own sitemap is complete and correct for this site's own pages, and
that is the scope being maintained here.

## Current state

As of 2026-09-22, read off the Page indexing report before the second fix
was deployed:

- 973 indexed pages, 107 not indexed. Both moved the right way since
  2026-09-07 (807 indexed, 218 not).
- Sitemap: 527 URLs, every one a real page, no redirect stubs listed.
- Of the 107 not indexed: 63 are Google's own crawl decisions (48
  "Discovered", 15 "Crawled"), 9 are intentionally `noindex` mdBook pages,
  and 35 are the four Website-sourced reasons -- 16 `Page with redirect`,
  12 `Not found (404)`, 6 `Duplicate without user-selected canonical`,
  1 `Alternate page with proper canonical tag`.

Of those 35, the 2026-09-22 fix addresses the genuine ones. Two are correct
as they stand and need no change: `/en/calendar/` under *Alternate page*, and
`http://www.veltzer.org/` under *Page with redirect*.

Note the `noindex` count went 4 -> 9, which is the drift toward 42 predicted
above as Google works through the 21 `rs*` mdBooks. Not a regression.
