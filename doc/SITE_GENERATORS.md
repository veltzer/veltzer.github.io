# Static site generators compared

rssite, MkDocs and the alternatives, judged for this site: a bilingual blog
(English and Hebrew), a media tracker and a few embedded apps, built by
rsconstruct and served from GitHub Pages.

The site has been built by three of them:

| Period | Generator | Why it ended |
| --- | --- | --- |
| until 2026-08 | MkDocs with Material | no way to have both the blog plugin and a second language |
| 2026-08 to 2026-10-16 | zola | it worked, through a long list of workarounds |
| since 2026-10-16 | rssite | current |

So the first three generator sections are written from use. The rest are
written from general knowledge of those tools, not from running them, and
none of their claims was re-checked against current releases for this
document: treat them as a starting point. The
decision records are in `doc/DECISIONS.md`, and rssite's own "Lessons from
zola" chapter (`docs/src/zola-problems.md` in the rssite repository) lists
every zola workaround this site carried.

## What turned out to matter

The first version of this document compared generators on ecosystem, themes
and "fits a Python pipeline". None of that decided anything. These did:

1. **Two languages as equals.** Each language under its own prefix, a post
   paired with its translation, tags that are translated and still linked
   to each other, dates and UI strings per language, right-to-left.
2. **Loud failure.** A missing translation, an unknown config key or a broken
   link must fail the build. A generator that exits 0 and quietly drops a
   page is worse than one that cannot do the thing at all.
3. **Transparency to the build system.** rsconstruct caches one product per
   output file and runs the linters over the rendered pages. That needs the
   generator to say what it will write, from which sources, before it writes.
4. **Reproducible output.** Two builds of the same commit must be identical,
   or nothing can be verified by diffing.
5. **No runtime.** One binary in CI: no Ruby, Node or Python environment to
   keep alive for the generator's sake.
6. **A blog.** Dated posts, tags, feeds, year archives, pagination, search.

## At a glance

| | rssite | MkDocs + Material | zola | Hugo | Jekyll | Eleventy | Pelican | Astro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Written in | Rust | Python | Rust | Go | Ruby | JavaScript | Python | JavaScript |
| Runtime needed | none | Python | none | none | Ruby | Node | Python | Node |
| Templates | Tera | Jinja2 | Tera | Go templates | Liquid | many | Jinja2 | components |
| Built for | this fleet's sites | documentation | sites and blogs | sites and blogs | blogs | anything | blogs | content sites |
| Blog out of the box | yes | plugin | yes | yes | yes | assemble it | yes | assemble it |
| Two languages | first-class | broke the blog | default-language bias | first-class | plugin | plugin | plugin | built-in routing |
| Translated, paired tags | yes | no | no | yes | no | by hand | no | by hand |
| Says what it will write | yes (`plan`) | no | no | no | no | no | no | no |
| Themes to pick from | none | one excellent | few | many | many | few | dated | many |
| Maintained by | one person | a team | a small team | a large project | a large project | a small team | volunteers | a company |

"Says what it will write" is the row no other generator fills, and the
reason rssite exists.

## rssite

The fleet's own generator: Rust, one binary, on crates.io. Written after the
zola period, with this site as its first user.

### Strengths of rssite

- `rssite plan` lists every file a build writes with the sources each
  depends on, and `build` is the same code run to the end. rsconstruct turns
  that into one cached product per file: an unchanged site runs rssite zero
  times, and an edited post rebuilds only the files that list it.
- It never deletes the output directory, so the companies data, the post
  share cards and the shared-themes files live in `_site/` beside its own.
- Languages are explicit and symmetrical. There is no default language: every
  file carries a suffix, every language a prefix, a title, a locale, a date
  format and a direction. Posts pair by file name, tags pair by position
  (`infer_translations`), and `require_translations` fails the build on an
  unpaired post.
- Strict by construction. An unknown key in `rssite.toml` or in front matter
  is an error, `get_url` fails on a file the build does not write, and
  `rssite check` renders the whole site twice in memory and reports every
  broken link, template or translation, and any difference between the two
  renders.
- Output is a function of the sources: no `now()`, the footer's date is the
  commit's.
- The things this site kept writing by hand are built in: the meta
  description, the post's JSON-LD, related posts, year archives, feeds per
  language and per tag, the sitemap, the search index, `[[publish]]` for
  files from a submodule, `[cascade]` for front matter a section hands down.
- `rssite query` prints the parsed site as JSON, so scripts do not re-parse
  front matter.
- When it lacks something, the fix is a release away. Three were cut in two
  days in 2026-11 for this site (0.1.28: the author `@id` and post images;
  0.1.29: Hebrew feed titles and author; 0.1.31: `highlight_css`).

### Weaknesses of rssite

- One maintainer and, so far, one family of sites using it. Nobody else has
  found its bugs, and nobody else will fix them.
- No themes to choose from and no plugin system. Every template here was
  written for this site.
- No community: no answers to search for, no third-party tutorials, and
  what documentation there is, is its own.
- Young. Its behaviour is what this site needed; a site with different needs
  will hit the edges first.
- A site built on it is tied to this fleet. Moving away means rewriting the
  templates, although Tera templates port to zola with moderate work.

**Verdict:** the right tool here because the fleet owns it and the two things
this site needs most, equal languages and a plan, are its design centre. It
would be a poor recommendation to anyone outside the fleet.

## MkDocs with Material

Python, built for documentation; the blog is a plugin of the Material theme.
The site ran on it until 2026-08.

### Strengths of MkDocs with Material

- Material is the best-looking theme of any generator here, with no CSS work.
- Small configuration, Markdown with good extensions (admonitions, tabs).
- Search built in, navigation generated from the directory tree.
- Python plugins are easy to write.

### Weaknesses of MkDocs with Material

- The blog is secondary, and it showed: no real taxonomies beyond what the
  plugin offers, and a full rebuild on every run.
- **It cannot do a bilingual blog.** `mkdocs-static-i18n` and the blog plugin
  are incompatible, and the failure is silent: the build exits 0 and emits no
  post pages. This is what ended it here (`doc/IMPROVEMENTS.md`,
  "Internationalization").
- The Material team has warned that MkDocs 2.0 breaks plugins and theme
  overrides with no migration path (`doc/DECISIONS.md`).
- Needs a Python environment for the generator, and the theme's HTML is not
  yours to shape.

**Verdict:** still the easy answer for single-language documentation. Not for
a blog in two languages.

## zola

Rust, one binary, Tera templates, Sass and syntax highlighting built in. The
site ran on it from 2026-08 to 2026-10-16.

### Strengths of zola

- No runtime, fast, simple TOML configuration.
- A real blog: sections, taxonomies, feeds, pagination, a search index.
- Tera is close to Jinja2, so the MkDocs-era template knowledge carried over.

### Weaknesses, all met in use

- One language is the default: it has no suffix and lives at the root, and
  the others are second-class. `foo.en.md` under an English default built
  `/blog/foo-en/`.
- Taxonomy terms have no link to their translation, the order of
  `page.translations` was not deterministic, and the `date` filter ignored
  `locale`.
- An unpaired translation loses its language switcher with no error; an
  English tag on a Hebrew post creates a new term with no error.
- It cannot say what it will write. rsconstruct's zola processor reimplemented
  zola's path logic in about 1,700 lines to cache its output per file.
- `zola build` deletes its output directory first, so everything else that
  writes into `_site/` had to be staged around it.
- Version churn: 0.23 renamed the highlighting configuration and changed the
  highlighter, so an unpinned upgrade failed on `config.toml` alone.

**Verdict:** a good generator for a single-language site that is built by
running `zola build` and nothing else. Each weakness above was survivable; the
sum was a build held together by workarounds.

## Hugo

Go, one binary, the most widely used generator of this kind.

### Strengths of Hugo

- Very fast, no runtime, large community and theme catalogue.
- Multilingual is first-class and the closest to what this site needs:
  languages with their own configuration, weight and direction, translations
  paired by file name or by `translationKey`, and translated taxonomies.
- Asset pipeline built in (Sass, image processing, fingerprinting).
- Taxonomies, archetypes, shortcodes, output formats.

### Weaknesses of Hugo

- Go templates are hard to read and harder to debug; the template lookup
  order is a subject of its own.
- No plan: it writes what it writes, and a build system sees one opaque
  step.
- Lenient by default: many mistakes are warnings.
- Releases are frequent and sometimes breaking, so the version must be pinned.

**Verdict:** the strongest alternative, and the one to move to if rssite were
abandoned: its multilingual model is the only other one here that pairs
translated tags. The price is the template language and an opaque build.

## Jekyll

Ruby; the generator GitHub Pages runs natively.

### Strengths of Jekyll

- Push and it builds: no CI needed on GitHub Pages.
- Built for blogging from the start: posts, drafts, categories, tags,
  pagination.
- Huge theme ecosystem and documentation.

### Weaknesses of Jekyll

- Ruby and Bundler environments are a recurring cost.
- Slow on large sites.
- GitHub Pages runs an old version with a fixed plugin list, so anything
  beyond the basics needs CI anyway.
- No multilingual support of its own; it comes from plugins that GitHub's
  native build does not allow.

**Verdict:** only attractive for its zero-CI deployment, which this site
gave up long ago by having a build.

## Eleventy

JavaScript; a small, flexible core with a choice of template languages.

### Strengths of Eleventy

- No opinions about structure, fast builds, good incremental support.
- Any template language (Nunjucks, Liquid, and more).
- The whole npm ecosystem is available.

### Weaknesses of Eleventy

- Needs Node, which this site's build deliberately does not have.
- Nothing is given: pagination, tags, feeds and a theme are assembled by hand.
- Internationalisation is a plugin that helps with URLs and leaves the
  pairing of content to the site.

**Verdict:** a good base for someone who wants to build their own generator
out of parts. Here that role is taken.

## Pelican

Python; built for blogging.

### Strengths of Pelican

- Posts, categories, tags and feeds are first-class.
- Jinja2 templates and Python plugins.
- Markdown and reStructuredText.

### Weaknesses of Pelican

- Small community, slow development, dated themes.
- No search of its own.
- Translations exist, but a full bilingual site is a plugin's job.

**Verdict:** would have been the natural step from MkDocs when the build
pipeline was Python. It is not any more.

## Astro, and the React frameworks

Astro is a JavaScript framework for content sites that ships HTML and adds
scripts only where a component asks for them. Gatsby and Next.js (static
export) are React frameworks that can also emit a static site.

### Strengths of Astro and the React frameworks

- A component model, for pages that are really applications.
- Astro has typed content collections and built-in routing per language.
- Image optimisation and modern tooling.

### Weaknesses of Astro and the React frameworks

- Node and a large dependency tree, at build time and to keep up to date.
- Far more machinery than a blog needs; Gatsby and Next.js also ship a
  large client-side bundle.
- Gatsby's development has slowed.
- Opaque to a build system, like the rest.

**Verdict:** Astro would be the pick for a site made of interactive
components. This site is text with a few self-contained apps, and those are
plain scripts.

## How the choices were made

- **MkDocs, originally:** the build pipeline was Python, Material looked
  finished without any work, and the site was documentation-shaped. All true,
  and none of it about being a bilingual blog, which the site became later.
- **zola, 2026-08:** the Hebrew translation needed real multilingual support
  and MkDocs could not provide it with the blog plugin. Why zola and not
  Hugo was not written down at the time.
- **rssite, 2026-10-16:** the zola build worked through a growing list of
  workarounds, the largest being rsconstruct's reimplementation of zola's
  path logic. Writing a generator whose first property is that it says what
  it will write was less work than carrying those.

The lesson for the next comparison: list what the site must do, in order of
how badly a failure would hurt, before listing what each tool offers.
