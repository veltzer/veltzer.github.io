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
| --- | --- | --- |
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
  `shared-themes`) for the logo tile, the portrait's ring, the author's
  name on a post card, `veltzer.org` and an 18px band along the bottom.
- **Everything that matters is centred inside the middle square** of the
  card (630x630, see below): the portrait at the top, the text under it in
  a column 570px wide.
- **The author's portrait** in a circle, 210px on a post card and 270px on
  a site-wide one, which has less to say.
- Outside the square, only the corners: the logo top left and `veltzer.org`
  bottom right (mirrored in Hebrew).
- Site-wide card: under the portrait the name, as large as fits the column
  on one line (84px at most), then the line under it, wrapped.
- Post card: under the portrait the author's name, small, in the accent;
  then the title at the largest of 72 down to 32px at which it fits its box
  in at most five lines (cut with an ellipsis beyond that; the longest
  title, 107 characters, fits); then the tags joined by `·`, as many of the
  first ones as fit one line.
- Wrapped text is balanced: the lines of a title are of about one length,
  never three full lines and a stray word.

## The middle square (2026-11-27)

A preview takes one of two forms, and the platform chooses. The large one
shows the whole card. The small one, a thumbnail beside the title, shows
only a square cut from the middle of it: 630 of the 1200 pixels.

Until 2026-11-27 the cards were laid out across the full width, the text
on one side and the portrait on the other. The small form then showed the
middle of the title, its words cut at both ends, and a sliver of the face.
Now the square is the card: the portrait and every word are inside it, so
the small form shows a whole picture, with the face at its top, which is
the one thing still readable at thumbnail size. The price is paid by the
large form, whose two sides carry only the logo and `veltzer.org`, and
whose title is set in a narrower column and so somewhat smaller.

One picture has to serve both forms: a page names one `og:image`, and
nothing tells a platform to use a second, square one for its thumbnail.

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
bundle; both scripts refuse to run without it). The middle square is
centred, so only the corners mirror: the logo moves to the top right and
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

## Seeing a card

`scripts/show_card.py <post>` shows the card of one post, named by its
file, by its slug (`--lang he` for a language other than English) or by any
URL of the site:

```sh
scripts/show_card.py why-the-faithful-lie
scripts/show_card.py content/blog/2026-11-27-why-the-faithful-lie.he.md
scripts/show_card.py --local why-the-faithful-lie
```

It reads the page with WhatsApp's user agent, prints the `og:` tags, fetches
the picture `og:image` names, checks what a platform would trip over (the
size, the dimensions, a missing tag) and opens a mock-up of the two forms a
preview takes, the large one and the small one, with the middle square the
small one is cut from shown enlarged beside them. It asks the live site,
which is what a link shared now shows; `--local` reads `_site/` after a
build, to look before pushing.

The script shows the card as it is now, not what a platform has cached.

The platforms cache a link's preview, some for days. After a card changes,
a link already shared keeps its old card until the platform fetches it
again; LinkedIn's Post Inspector and Facebook's Sharing Debugger force a
fresh fetch, and WhatsApp refreshes on its own schedule.
