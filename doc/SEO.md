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

Both trace to the same history: the MkDocs-to-zola migration, and
`relocate_english()` later moving English content under `/en/`. They are
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

## Open: the two validations

Both issues were submitted for validation on 2026-09-07 and read
**Validation: Started** on the Page indexing report:

| Reason | Pages | Validation |
| --- | --- | --- |
| Not found (404) | 9 | Started |
| Page with redirect | 6 | Started |

Google recrawls the affected URLs and checks them against the deployed fix.
This takes days to a couple of weeks. The status becomes *Passed* if every URL
comes back clean, or *Failed* with the specific URLs that still fail.

Nothing to do while it runs. **If it comes back Failed, the failing URLs are
the thing to look at** -- the redirects and sitemap were verified correct and
live, so a failure would mean something about Google's crawl rather than the
build, and the specific URLs would say what.

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

As of 2026-09-07, after the fix:

- 807 indexed pages, 218 not indexed.
- Sitemap: 517 URLs, every one a real page.
- Of the 218 not indexed: 199 are Google's own crawl decisions, 4 are
  intentionally `noindex`, and 15 are the two issues now under validation.
