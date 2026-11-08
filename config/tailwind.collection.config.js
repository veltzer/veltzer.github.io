// Tailwind 3 configuration for the data collection app (templates/data_collection.html), compiled
// by scripts/build_collection_css.sh into static/vendor/tailwind-collection.css. It
// used to run in the browser through Tailwind's CDN compiler; the palette and
// options below are what that page set as `tailwind.config`, unchanged.
//
// The data collection app's markup uses Tailwind colour utilities (bg-white,
// text-gray-500, text-blue-600 and so on), which are fixed colours and so
// ignored the site theme. Rather than rewrite two dozen classes across the
// plugins, the palette itself is redefined in terms of the theme tokens: every
// existing utility then resolves to a var() and follows the theme switcher.
//
// The scale is mapped by role, not by lightness -- 50/100/200 are the surface
// steps, 500+ are text -- so the same class means the same thing in a light or
// a dark theme instead of inverting.
//
// The same goes for shape: the corner radii and shadows are the theme's
// --radius-* and --shadow tokens, and the gray-200/300 border colours are the
// site's --border-subtle/--border, so a card or a pill here is drawn like the
// boxes and tags on the rest of the site.
module.exports = {
content: [
  "templates/data_collection.html",
  "static/data-collection-app.js",
  "static/data-collection-utils.js",
  "static/plugin-*.js",
],
important: '#collection-root',
corePlugins: { preflight: false },
theme: {
  extend: {
    borderRadius: {
      sm: 'var(--radius-xs)',
      DEFAULT: 'var(--radius-xs)',
      md: 'var(--radius-sm)',
      lg: 'var(--radius-sm)',
      xl: 'var(--radius)',
      full: 'var(--radius-pill)'
    },
    boxShadow: {
      sm: 'none',
      DEFAULT: 'var(--shadow)',
      md: 'var(--shadow)',
      lg: 'var(--shadow)'
    },
    borderColor: {
      gray: {
        200: 'var(--border-subtle)',
        300: 'var(--border)'
      }
    },
    colors: {
      white: 'var(--bg)',
      black: 'var(--text-primary)',
      gray: {
        50: 'var(--bg-surface)',
        100: 'var(--bg-surface)',
        200: 'var(--bg-elevated)',
        300: 'var(--border)',
        400: 'var(--text-muted)',
        500: 'var(--text-secondary)',
        600: 'var(--text-secondary)',
        700: 'var(--text-primary)',
        800: 'var(--text-primary)',
        900: 'var(--text-primary)'
      },
      blue: {
        50: 'var(--bg-surface)',
        100: 'var(--bg-elevated)',
        400: 'var(--accent)',
        500: 'var(--accent)',
        600: 'var(--accent)',
        700: 'var(--accent)',
        800: 'var(--accent)'
      },
      red: {
        100: 'var(--bg-surface)',
        400: 'var(--danger, #dc2626)',
        600: 'var(--danger, #dc2626)',
        700: 'var(--danger, #dc2626)'
      },
      green: {
        100: 'var(--bg-surface)',
        600: 'var(--success, #16a34a)',
        700: 'var(--success, #16a34a)'
      }
    }
  }
}
};
