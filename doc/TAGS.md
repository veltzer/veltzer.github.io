# Tags

Everything about the blog's tags in one place: how they work, what was
decided and why, what the build enforces, and the questions still open.
Other documents touch tags in passing and link here; the Russian tag
glossary stays in `doc/TRANSLATION.md` with the rest of the translation.

## How tags work today

- **One taxonomy**, `tags`, declared under `[[taxonomies]]` in `rssite.toml`
  with `feed = true`, `paginate_by = 20` and `infer_translations = true`.
- **Front matter**: a post lists its tags under `[taxonomies]`, as in
  `tags = ["religion", "philosophy", "ethics"]`.
- **Pages generated per language**: the tag list `/<lang>/tags/`
  (`templates/taxonomy_list.html`, a tag cloud with counts), one page per tag
  `/<lang>/tags/<tag>/` (`templates/taxonomy_single.html`), its pagers
  `/<lang>/tags/<tag>/page/N/` and its feed `/<lang>/tags/<tag>/atom.xml`.
- **Where tags show**: the post header (`templates/page.html`, each tag a
  link through `page.taxonomies.tags[].permalink`), the related posts under
  a post (`page.related`, ranked by shared tags), the post's JSON-LD (tags as
  `keywords`), the per-post share card (tags joined by `·`, see
  `doc/SHARE_CARDS.md`), the `og:title` of tag pages (`term.name`,
  `templates/base.html`) and the blog search, where `simple` mode matches
  titles, opening text and tags (`<lang>/search.json`).
- **Strings**: `nav_tags`, `tags_title` and `tagged_with` in
  `i18n/<lang>.toml`; the nav entry is `{ key = "nav_tags", path = "tags/" }`
  in `[extra.nav]`.

### Numbers (2026-11-23)

- 441 posts, 63 tags per language. Tags per post: 3 on 272 posts, 2 on 107,
  4 on 51, 5 on 4, 6 on 1, 1 on 5, none on 1. 8 tags are used by a single post.
- Most used: politics 159, religion 111, philosophy 103, epistemology 88,
  direct-democracy 79, opinion 71, history 69, science 62.
- Output per language: 172 files (63 tag pages, 63 feeds, 45 pagers, the
  list), 6.8 MB English, 8.2 MB Hebrew, 9.6 MB Russian. Of the English
  6.8 MB the **feeds are 5.2 MB** (full post content in each), the tag pages
  0.6 MB and the pagers 0.5 MB.
- The sitemap lists 192 tag URLs (63 tags and the list, times three
  languages), each with its hreflang alternates. Pagers are not listed
  (`[sitemap] pagers = false`, see `doc/SEO.md`).

## Decisions

### Tags are translated; post slugs are not

`/en/tags/religion/` is `/he/tags/דת/` and `/ru/tags/религия/`, while a post
keeps one English slug in every language. Tags are short, reader-facing and
browsed as a list, so English words on `/he/tags/` were plainly wrong in a
way an opaque post URL is not. Tags are not a shared key (posts pair by file
name), so translating them costs nothing structurally. The full reasoning,
with the post side of it, is in `doc/DECISIONS.md` under "Post slugs are
shared between languages; tag slugs are not".

Hebrew and Russian tags keep their letters in the URL:
`[slugify] taxonomies = "safe"` in `rssite.toml`. A transliterating slugify
would turn ארכיאולוגיה into `rky-vlvgyh`. One consequence when moving to
rssite: the geresh in `ג׳אווה` is not a slug character, so that tag's URL
changed (not preserved, by decision; `doc/DECISIONS.md`).

### Tags pair by position

A post and its translations list their tags in the same order, and position
N in one list is the translation of position N in the other. rssite pairs the
terms that way (`infer_translations`), which gives every tag page its
language switcher and hreflang alternates with no lookup table. A pair whose
lists differ in length, or a tag that lines up with two different
counterparts, fails the build. This replaced zola's generated translation
table and template lookup (`doc/DECISIONS.md`, the rssite migration).

Russian tags come from the fixed glossary in `doc/TRANSLATION.md` ("Tag
glossary"): an English tag always maps to the same Russian tag, and a new
English tag gets a glossary entry.

### Technical names stay Latin

A few tags are technology names and stay as they are in every language:
`LATIN_TAGS = {"mysql", "php"}` in `scripts/check_hebrew.py`. Others (gpg,
ssh, mkdocs, github-pages) were translated.

### Topical, not by language

`hebrew` used to tag posts only because they were written in Hebrew. Since
2026-10-29 it is only on "Hebrew on Linux", where Hebrew is the subject, so
the vocabulary is all topical (`doc/IMPROVEMENTS.md`).

### About three tags per post

The convention is about three tags per post. When the 2026 religion sequence
had a single tag (`religion`) on 33 posts, they were given 1-2 topical tags
each; `atheism` was deliberately left off the ~40 posts that argue that
position, as a statement about self-labelling. The tag vocabulary is an
editorial call and changes to it are proposed to the author first
(`doc/IMPROVEMENTS.md`, "The 3-tag convention was abandoned").

### Share cards do not use a picture per tag

A picture per tag (the card showing its post's first tag) was one of the
four options for the share cards' picture, and was not chosen: every card
carries the author's portrait (`doc/SHARE_CARDS.md`).

## What the build checks

- **Pairing**: `infer_translations` fails on lists of different lengths or
  a tag that pairs with two counterparts.
- **Hebrew tags are Hebrew**: `scripts/check_hebrew.py` fails on a tag of a
  Hebrew post that is neither Hebrew nor in `LATIN_TAGS`, and on English in
  the built Hebrew feeds, the tag feeds among them (they once carried the
  English site title; fixed in rssite 0.1.29, `doc/TRANSLATION.md`).
- **Not checked**: Russian tags have no such check; only the glossary and the
  pairing keep them consistent.

## Open question: one page instead of a page per tag

Asked 2026-11-23: instead of a page per tag per language, could there be one
page per language, or one page for all languages, that loads a "db" of
tag -> posts and renders the chosen tag in JavaScript? Nothing was changed;
these are the considerations.

**The data already exists.** `<lang>/search.json`, which the blog search
loads, lists every post's tags. A JS view (for example `/en/blog/?tag=religion`,
reusing `static/blog-search.js`) needs no new build step.

**What it would save.** Little: the tag HTML pages and pagers are about
1 MB per language, and the build is incremental (a new post rebuilds only its
own tags' pages; an unchanged site runs rssite zero times). The bulk of the
tag output is the feeds, which a JS page cannot replace anyway.

**What a JS view loses:**

1. **Search indexing.** The 192 tag URLs in the sitemap are landing pages.
   A `?tag=` or `#tag` view is one URL to a search engine.
2. **Per-tag feeds.** A feed reader needs a static file per tag, so
   subscribing to one subject either keeps static feeds or goes.
3. **Language pairing.** The switcher on `/en/tags/religion/` reaches
   `/he/tags/דת/` through `infer_translations`; in JS it would be rebuilt by
   hand.
4. **No JavaScript, print, share cards.** The page is empty without JS, and
   its `og:title` cannot name the tag.

**One page for all languages** is worse: the tags are translated, the page
strings differ and Hebrew is right to left, so there would still be a shell
per language; only the data would be shared, and it is not a real cost.

**The cheaper lever if size matters is the feeds**, about 75% of the tag
output: make the tag feeds summaries instead of full content, or drop them
(`feed = false` on the taxonomy) and keep the per-language blog feed. That
keeps the indexable, paired, no-JS tag pages.

**Recommendation at the time**: leave the tag pages as they are; if the
output size is ever the concern, change the feeds first.
