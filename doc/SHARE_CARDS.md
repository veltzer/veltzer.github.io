# Share cards

The image a chat app or social network (WhatsApp, Slack, X, LinkedIn,
Facebook, Telegram, ...) shows beside a shared link. Every page of the site
names one in `og:image`, 1200x630 with `twitter:card = summary_large_image`;
without it a shared link gets a bare text preview, or a picture the
platform picks off the page itself.

This file records what the cards are, how they are made, and why they look
the way they do.

## Two kinds of card

| | Site-wide cards | Post cards |
|---|---|---|
| Used by | every page that is not a post: the home page, About, the tag and archive pages, the apps, the root language chooser | each blog post, in each language |
| Files | `static/images/og/card-{en,he,ru}.jpg`, one per language | `_site/images/og/<post file stem>.jpg`, e.g. `2026-04-28-euthyphro-dilemma.en.jpg` |
| Drawn by | `scripts/make_og_images.py`, by hand | `scripts/make_post_cards.py`, by the build (`processor.generator.generic.post_cards` in `rsconstruct.toml`) |
| Committed | yes | no, build output |
| Says | the name and the line under it, from `home_title` in `i18n/<lang>.toml` | the post's title and tags, the author's name |

The split is deliberate. The site-wide cards change only when `home_title`,
the colours or the portrait change, so they are drawn once and committed,
and the build needs nothing to produce them. The post cards are 440 posts
times three languages: committed, they would go stale the moment a title
changed. As build products, each card depends on its post, so editing a post
redraws its card and nothing else.

`templates/base.html` picks between them: a post has `page.image` (set for
every post by the `[cascade]` in `content/blog/_index.<lang>.md`), and
everything else falls back to its language's site-wide card.
`templates/root.html` uses the English site-wide card.

## The layout

Both kinds share one layout, and one module: `make_post_cards.py` imports
its constants and drawing helpers from `make_og_images.py`, so the two
cannot drift.

- White background, the default light theme's accent (`#4051b5`, azure in
  `shared-themes`) for the logo tile, the portrait's ring, `veltzer.org`
  and an 18px band along the bottom.
- Text on the near side of the reading direction, in a column 670px wide.
- **The author's portrait** in a 300px circle on the far side.
- `veltzer.org` bottom right (bottom left in Hebrew).
- Site-wide card: the logo large, then the name as large as fits the column
  on one line (96px at most), then the line under it, wrapped.
- Post card: the logo and the name small at the top, then the title at the
  largest of 76 down to 44px at which it fits four lines (cut with an
  ellipsis beyond that; the longest title, 107 characters, fits at the
  default sizes), then the tags joined by `·`.

The cards are not themed. A share card is seen outside the site, by people
who have not chosen a theme, and one fixed look is what makes it
recognisable from link to link. The light theme is the one that survives
being shown on both light and dark chat backgrounds.

## The portrait is on every card (2026-11-22)

Until 2026-11-22 the cards were lettering only. Shared in a feed, a
text-only card reads as a plain link; a picture is what catches the eye.
Four ways to give the cards a picture were weighed:

1. **The author's portrait on every card.** One picture, no work per post,
   and it says who wrote it, which is the point of a personal site.
2. **A picture per tag**, the card using its post's first tag. About 60
   pictures, once; the cards would show the subject rather than the author.
3. **An optional `image` key in a post's front matter**, for a post that
   deserves its own picture, falling back to 1 or 2 everywhere else.
4. **A generated picture per post**: abstract patterns from the slug (free
   but meaningless) or AI images (each one to be checked by hand).

Chosen: **1**, for both kinds of card. 3 stays open as an addition: a post
with its own picture would show it in place of the portrait. Hand-picking a
picture for every post was rejected outright: 440 posts, one of which has a
picture today, is a job that never ends, and a half-done set makes the
undone half look worse.

The portrait is `static/images/mark-veltzer.jpg`, the drawing on the About
page, so the site shows one face everywhere. It is cut to a circle with a
thin accent ring, drawn at four times the size and scaled down for a smooth
edge, and it is a declared input of the post cards (`dep_inputs` of
`post_cards`): replacing the file redraws every post card on the next
build. The site-wide cards need `make_og_images.py` run by hand.

## Right to left

Hebrew is laid out right to left (Pillow needs libraqm, which its wheels
bundle; both scripts refuse to run without it), and the whole card mirrors:
the text hangs from the right edge, the portrait moves to the left, and
`veltzer.org` to the bottom left.

## Fonts

English is set in Outfit, the site's heading font, from the
`shared-themes` submodule. Hebrew and Russian are set in Liberation Sans
(the `fonts-liberation` apt package, declared in `rsconstruct.toml`), which
has the Hebrew and Cyrillic letters Outfit lacks and the comma Noto Sans
Hebrew lacks. Pillow does no font fallback, so one font per language has to
cover the whole text. `veltzer.org` is always Outfit.

## Making changes

- Changed a post's title or tags: nothing to do, the build redraws its card.
- Changed `home_title`, the colours, the layout or the portrait: run
  `scripts/make_og_images.py` from the repository root and commit the three
  JPEGs; the build redraws the post cards itself.
- Look before committing: the cards are JPEGs, so open a few of them,
  including a Hebrew one and the longest title.

The platforms cache a link's preview, some for days. After a card changes,
a link already shared keeps its old card until the platform fetches it
again; LinkedIn's Post Inspector and Facebook's Sharing Debugger force a
fresh fetch, and WhatsApp refreshes on its own schedule.
