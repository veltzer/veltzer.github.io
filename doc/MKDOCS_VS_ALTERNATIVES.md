# MkDocs vs Alternative Static Blog Engines

Comparison of static site generators suitable for blogging on GitHub Pages.
Context: this project uses MkDocs with the Material theme.

---

## MkDocs (with Material for MkDocs)

**What it is:** Python-based static site generator, originally for documentation, with blog support via the Material theme's blog plugin.

### Advantages
- Python ecosystem — fits naturally into a Python-based build pipeline (pydmt, pymakehelper)
- Material for MkDocs theme is polished and feature-rich out of the box
- Simple config (`mkdocs.yml`) — minimal boilerplate
- Markdown-first with good extension support (admonitions, tabs, code blocks)
- Built-in search (lunr.js)
- Easy to extend with Python plugins
- Good navigation/sidebar generation from directory structure
- Active development and large community

### Disadvantages
- Blog support is secondary — MkDocs was designed for documentation, not blogging
- Material for MkDocs blog plugin is relatively new and less mature than dedicated blog engines
- MkDocs 2.0 will break all plugins and theme overrides (see DECISIONS.md)
- Limited taxonomies — no built-in tags/categories beyond what Material provides
- Rebuild is full-site (no incremental builds)
- Fewer blog-specific themes compared to Jekyll or Hugo

---

## Jekyll

**What it is:** Ruby-based static site generator. The default engine for GitHub Pages with native integration.

### Advantages
- Native GitHub Pages support — push and it builds automatically, no CI needed
- Mature blog engine — built for blogging from day one
- Huge theme ecosystem
- Liquid templating is straightforward
- Large community, extensive documentation
- Built-in support for posts, drafts, categories, tags, pagination
- Incremental builds available

### Disadvantages
- Ruby dependency — managing Ruby/Bundler environments is painful
- Slow builds on large sites
- Liquid templating is limited compared to Jinja2 or Go templates
- GitHub Pages runs an older Jekyll version with restricted plugins
- Not a natural fit for a Python-based project

---

## Hugo

**What it is:** Go-based static site generator. Known for speed.

### Advantages
- Extremely fast builds (milliseconds for hundreds of pages)
- Single binary — no runtime dependencies
- Powerful templating (Go templates)
- Built-in support for taxonomies, shortcodes, multilingual sites
- Good blog support with archetypes
- Active development, large community
- Asset pipeline built in (SCSS, JS bundling, image processing)

### Disadvantages
- Go template syntax is unintuitive and hard to debug
- Steeper learning curve than MkDocs or Jekyll
- No plugin system — extensibility is limited to templates and shortcodes
- No Python integration — would require a separate build step for Python tooling
- Theme customization can be complex (template lookup order)

---

## Pelican

**What it is:** Python-based static site generator designed for blogging.

### Advantages
- Python-native — same ecosystem as this project's build tools
- Built for blogging — first-class support for posts, categories, tags, feeds
- Jinja2 templating (same as MkDocs)
- Plugin system in Python
- Supports reStructuredText and Markdown
- Simple and lightweight

### Disadvantages
- Smaller community than Jekyll or Hugo
- Fewer themes available, most look dated
- Less active development in recent years
- No built-in search
- Documentation is adequate but not as polished as MkDocs Material

---

## Eleventy (11ty)

**What it is:** JavaScript-based static site generator. Flexible and minimal.

### Advantages
- Very flexible — supports multiple template languages (Nunjucks, Liquid, Handlebars, etc.)
- Fast builds
- No opinion on project structure — highly customizable
- JavaScript ecosystem access (npm packages)
- Good incremental build support
- Active development, growing community

### Disadvantages
- Requires Node.js — adds a runtime dependency (though this project already uses npm)
- No built-in theme — you build everything from scratch
- Less structured than MkDocs — more decisions to make upfront
- No Python integration
- Blog features must be assembled manually (pagination, tags, feeds)

---

## Gatsby / Next.js (static export)

**What it is:** React-based frameworks that can export static sites.

### Advantages
- Full React component model — powerful for interactive content
- Rich plugin ecosystem (Gatsby)
- GraphQL data layer (Gatsby) for pulling from multiple sources
- Image optimization built in
- Modern JavaScript tooling

### Disadvantages
- Massively over-engineered for a blog
- Heavy build times and large dependency trees
- Requires React knowledge
- Large client-side JavaScript bundle
- No Python integration
- Gatsby development has slowed significantly
- Complex configuration

---

## Zola

**What it is:** Rust-based static site generator. Single binary, fast.

### Advantages
- Single binary, no dependencies
- Very fast builds
- Built-in Sass compilation, syntax highlighting, search
- Simple config (TOML)
- Good blog support with taxonomies and feeds
- Tera templating (similar to Jinja2)

### Disadvantages
- Smaller community and fewer themes
- No plugin system
- No Python integration
- Less mature than Hugo or Jekyll
- Fewer integrations and extensions

---

## Why MkDocs for This Project

MkDocs was chosen because:
1. **Python ecosystem alignment** — the build pipeline already uses Python (pydmt, pymakehelper, pylint, mypy, ruff)
2. **Material theme quality** — polished, responsive, feature-rich without custom CSS/JS work
3. **Simplicity** — minimal config, Markdown content, directory-based navigation
4. **Dual purpose** — serves both documentation and blog content well
5. **Jinja2/Mako compatibility** — templating style is consistent with pydmt's Mako templates

The main risk is the MkDocs 2.0 migration (see `DECISIONS.md`). If that becomes unmanageable, **Hugo** (for speed and maturity) or **Pelican** (for Python ecosystem fit) would be the strongest alternatives.
