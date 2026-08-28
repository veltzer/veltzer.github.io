+++
title = "Teaching Slides"
template = "app.html"
+++

<style>
#app-slides {
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius: 10px;
  --radius-pill: 20px;
  --transition: 180ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms ease;
  --font-sans: 'Outfit', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --shadow: 0 1px 3px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.25);
}
#app-slides, [data-theme="azure"] #app-slides {
  --bg: #ffffff;
  --bg-surface: #f5f5f7;
  --bg-elevated: #eaeaef;
  --bg-hover: #dcdce5;
  --border: #d0d0db;
  --border-subtle: #ececf2;
  --text-primary: rgba(0, 0, 0, 0.87);
  --text-secondary: rgba(0, 0, 0, 0.54);
  --text-muted: rgba(0, 0, 0, 0.32);
  --accent: #4051b5;
  --accent-dim: rgba(64, 81, 181, 0.12);
  --success: #1c7d4d;
  --success-dim: rgba(28, 125, 77, 0.12);
  --warning: #b87d1a;
  --warning-dim: rgba(184, 125, 26, 0.12);
  --danger: #c72c34;
  --danger-dim: rgba(199, 44, 52, 0.12);
  --gradient-start: #303fa1;
  --gradient-end: #526cfe;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
}
[data-theme="paper"] #app-slides {
  --bg: #faf8f5;
  --bg-surface: #f0ede8;
  --bg-elevated: #e8e4de;
  --bg-hover: #ddd8d0;
  --border: #cdc6bb;
  --border-subtle: #e0dbd4;
  --text-primary: #2c2824;
  --text-secondary: #706860;
  --text-muted: #a09888;
  --accent: #9b6b3e;
  --accent-dim: rgba(155, 107, 62, 0.12);
  --success: #3a8a5c;
  --success-dim: rgba(58, 138, 92, 0.12);
  --warning: #b87d1a;
  --warning-dim: rgba(184, 125, 26, 0.12);
  --danger: #c05040;
  --danger-dim: rgba(192, 80, 64, 0.12);
  --gradient-start: #2c2824;
  --gradient-end: #9b6b3e;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
}
[data-theme="midnight"] #app-slides {
  --bg: #0f1117;
  --bg-surface: #161922;
  --bg-elevated: #1e2130;
  --bg-hover: #252940;
  --border: #2a2e3f;
  --border-subtle: #1e2130;
  --text-primary: #e8eaf0;
  --text-secondary: #8b90a0;
  --text-muted: #5c6070;
  --accent: #6c8cff;
  --accent-dim: rgba(108, 140, 255, 0.12);
  --success: #34d399;
  --success-dim: rgba(52, 211, 153, 0.12);
  --warning: #fbbf24;
  --warning-dim: rgba(251, 191, 36, 0.12);
  --danger: #f87171;
  --danger-dim: rgba(248, 113, 113, 0.12);
  --gradient-start: #e8eaf0;
  --gradient-end: #6c8cff;
}
[data-theme="nord"] #app-slides {
  --bg: #2e3440;
  --bg-surface: #3b4252;
  --bg-elevated: #434c5e;
  --bg-hover: #4c566a;
  --border: #4c566a;
  --border-subtle: #434c5e;
  --text-primary: #eceff4;
  --text-secondary: #d8dee9;
  --text-muted: #7b88a1;
  --accent: #88c0d0;
  --accent-dim: rgba(136, 192, 208, 0.15);
  --success: #a3be8c;
  --success-dim: rgba(163, 190, 140, 0.15);
  --warning: #ebcb8b;
  --warning-dim: rgba(235, 203, 139, 0.15);
  --danger: #bf616a;
  --danger-dim: rgba(191, 97, 106, 0.15);
  --gradient-start: #eceff4;
  --gradient-end: #88c0d0;
}
[data-theme="solarized"] #app-slides {
  --bg: #fdf6e3;
  --bg-surface: #eee8d5;
  --bg-elevated: #e6dfcb;
  --bg-hover: #ddd6c1;
  --border: #d0c8b0;
  --border-subtle: #e6dfcb;
  --text-primary: #073642;
  --text-secondary: #586e75;
  --text-muted: #93a1a1;
  --accent: #268bd2;
  --accent-dim: rgba(38, 139, 210, 0.12);
  --success: #859900;
  --success-dim: rgba(133, 153, 0, 0.12);
  --warning: #b58900;
  --warning-dim: rgba(181, 137, 0, 0.12);
  --danger: #dc322f;
  --danger-dim: rgba(220, 50, 47, 0.12);
  --gradient-start: #073642;
  --gradient-end: #268bd2;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
}
[data-theme="rosepine"] #app-slides {
  --bg: #191724;
  --bg-surface: #1f1d2e;
  --bg-elevated: #26233a;
  --bg-hover: #312e47;
  --border: #393552;
  --border-subtle: #26233a;
  --text-primary: #e0def4;
  --text-secondary: #908caa;
  --text-muted: #6e6a86;
  --accent: #c4a7e7;
  --accent-dim: rgba(196, 167, 231, 0.14);
  --success: #9ccfd8;
  --success-dim: rgba(156, 207, 216, 0.14);
  --warning: #f6c177;
  --warning-dim: rgba(246, 193, 119, 0.14);
  --danger: #eb6f92;
  --danger-dim: rgba(235, 111, 146, 0.14);
  --gradient-start: #e0def4;
  --gradient-end: #c4a7e7;
}




@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
#app-slides {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text-primary);
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 28px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  transition: background var(--transition-slow), color var(--transition-slow);
}
#app-slides a {
  color: var(--accent);
  text-decoration: none;
  transition: color var(--transition);
}
#app-slides a:hover { color: var(--text-primary); text-decoration: underline; }
#app-slides hr {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 48px 0 16px 0;
}
#app-slides ::-webkit-scrollbar { width: 8px; }
#app-slides ::-webkit-scrollbar-track { background: var(--bg); }
#app-slides ::-webkit-scrollbar-thumb { background: var(--border); border-radius: var(--radius-xs); }
#app-slides ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }


@media (max-width: 700px) {
  body { padding: 20px 16px; }

}
#app-slides h1 {
  font-weight: 700;
  font-size: 2rem;
  letter-spacing: -0.03em;
  margin: 0;
  padding: 0;
  border: none;
  background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
#app-slides h2 {
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 32px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}
#app-slides h2 a { color: var(--accent); text-decoration: none; }
#app-slides h2 a:hover { color: var(--text-primary); }
#app-slides h2 .count { color: var(--text-muted); text-transform: none; letter-spacing: normal; font-weight: 400; }
#app-slides #total-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 400;
  margin: 0 0 28px 0;
  letter-spacing: 0.02em;
}
#app-slides .subtitle {
  color: var(--text-secondary);
  margin: 0 0 2rem 0;
}
#app-slides .count {
  color: var(--text-muted);
  font-size: 0.9em;
}
#app-slides .no-results {
  color: var(--text-muted);
  font-style: italic;
  padding: 40px 0;
  text-align: center;
}
#app-slides .build-info {
  font-size: 0.85em;
  opacity: 0.7;
  margin-top: 0.2em;
}
#app-slides .build-info code {
  background: transparent;
  padding: 0;
  font-size: 0.95em;
}


@media (max-width: 700px) {
  h1 { font-size: 1.5rem; }

}
#app-slides .header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 4px;
}
#app-slides #theme-select { flex-shrink: 0; }
#app-slides .filters {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  padding: 20px 24px;
  border-radius: var(--radius);
  margin-bottom: 28px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px 20px;
  transition: background var(--transition-slow), border-color var(--transition-slow);
}
#app-slides .filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}
#app-slides .filter-row-sort {
  grid-column: 1 / -1;
  flex-wrap: wrap;
}
#app-slides .filter-row label {
  font-weight: 500;
  font-size: 0.82rem;
  color: var(--text-secondary);
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
#app-slides select, #app-slides input[type="text"] {
  font-family: var(--font-sans);
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  font-size: 0.88rem;
  transition: border-color var(--transition), box-shadow var(--transition), background 350ms ease, color 350ms ease;
  outline: none;
}
#app-slides select:focus, #app-slides input[type="text"]:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
#app-slides input[type="text"] { width: 240px; }
#app-slides select { cursor: pointer; }
#app-slides .toggle-switch { position: relative; display: inline-block; width: 36px; height: 20px; vertical-align: middle; }
#app-slides .toggle-switch input { opacity: 0; width: 0; height: 0; }
#app-slides .toggle-slider {
  position: absolute; cursor: pointer; inset: 0;
  background: var(--border); border-radius: var(--radius-pill);
  transition: background var(--transition);
}
#app-slides .toggle-slider:before {
  content: ""; position: absolute;
  height: 14px; width: 14px; left: 3px; bottom: 3px;
  background: var(--text-secondary); border-radius: 50%;
  transition: transform var(--transition), background var(--transition);
}
#app-slides .toggle-switch input:checked + .toggle-slider { background: var(--accent); }
#app-slides .toggle-switch input:checked + .toggle-slider:before { transform: translateX(16px); background: var(--bg); }
#app-slides #breadcrumb { margin-bottom: 12px; font-size: 0.88rem; }
#app-slides #breadcrumb a { color: var(--accent); text-decoration: none; }
#app-slides #breadcrumb a:hover { color: var(--text-primary); }
#app-slides .breadcrumb-sep { color: var(--text-muted); margin: 0 6px; }
#app-slides .breadcrumb-current { font-weight: 600; color: var(--text-primary); }
#app-slides #subfolders { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
#app-slides #subfolders:empty { margin-bottom: 0; }
#app-slides .subfolder-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--text-primary);
  text-decoration: none;
  transition: background var(--transition), border-color var(--transition), transform var(--transition), box-shadow var(--transition);
}
#app-slides .subfolder-card:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
  text-decoration: none;
}
#app-slides .subfolder-count { color: var(--text-muted); font-weight: 400; font-size: 0.82rem; }
#app-slides ul { list-style: none; padding: 0; margin: 0; }
#app-slides li {
  padding: 10px 16px;
  margin: 0;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  transition: background var(--transition);
}
#app-slides li:hover { background: var(--bg-elevated); }
#app-slides li.hidden { display: none; }
#app-slides li a {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition);
}
#app-slides li a:hover { color: var(--accent); }
#app-slides .level, #app-slides .chapters-badge, #app-slides .slides-badge, #app-slides .duration, #app-slides .tag, #app-slides .type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}
#app-slides .level-beginner { background: var(--accent-dim); color: var(--accent); opacity: 0.7; }
#app-slides .level-intermediate { background: var(--accent-dim); color: var(--accent); opacity: 0.85; }
#app-slides .level-advanced { background: var(--accent-dim); color: var(--accent); }
#app-slides .tag { background: var(--accent-dim); color: var(--accent); }
#app-slides .chapters-badge { background: var(--accent-dim); color: var(--accent); opacity: 0.7; }
#app-slides .slides-badge { background: var(--accent-dim); color: var(--accent); }
#app-slides .duration { background: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border-subtle); }
#app-slides .type-badge { background: var(--success-dim); color: var(--success); text-transform: capitalize; }
#app-slides .type-course { background: var(--success-dim); color: var(--success); }
#app-slides .type-lecture { background: var(--warning-dim); color: var(--warning); }
#app-slides .course-number {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 400;
  min-width: 2.5em;
  display: inline-block;
}
#app-slides .stat-chapters { color: var(--text-secondary); font-weight: 600; }
#app-slides .stat-slides { color: var(--accent); font-weight: 600; }
#app-slides .dl-icon {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  color: var(--text-muted);
  transition: color var(--transition), transform var(--transition);
}
#app-slides .dl-icon:hover { color: var(--accent); transform: scale(1.15); }
#app-slides .dl-icon svg { width: 18px; height: 18px; }
#app-slides .autocomplete-wrap { position: relative; display: inline-block; }
#app-slides .autocomplete-list {
  position: absolute; top: 100%; left: 0; right: 0;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  max-height: 280px;
  overflow-y: auto;
  z-index: 100;
  display: none;
  box-shadow: var(--shadow);
}
#app-slides .autocomplete-list.visible { display: block; }
#app-slides .autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background var(--transition);
}
#app-slides .autocomplete-item:hover, #app-slides .autocomplete-item.active { background: var(--bg-hover); }
#app-slides .autocomplete-item .ac-folder { color: var(--text-muted); font-size: 0.78rem; margin-left: 8px; }



@media (max-width: 700px) {
  .header-bar { flex-direction: column; gap: 10px; }
#app-slides .filters { grid-template-columns: 1fr; padding: 16px; }
#app-slides input[type="text"] { width: 100%; }
#app-slides li { padding: 8px 10px; }

}
#app-slides {
  --md-sys-color-primary: var(--accent);
  --md-sys-color-on-primary: var(--bg);
  --md-sys-color-primary-container: var(--accent-dim);
  --md-sys-color-on-primary-container: var(--accent);
  --md-sys-color-secondary: var(--accent);
  --md-sys-color-surface: var(--bg);
  --md-sys-color-on-surface: var(--text-primary);
  --md-sys-color-surface-variant: var(--bg-surface);
  --md-sys-color-on-surface-variant: var(--text-secondary);
  --md-sys-color-surface-container: var(--bg-elevated);
  --md-sys-color-surface-container-high: var(--bg-elevated);
  --md-sys-color-surface-container-highest: var(--bg-hover);
  --md-sys-color-outline: var(--border);
  --md-sys-color-outline-variant: var(--border-subtle);
  --md-sys-color-error: var(--danger);

  --md-ref-typeface-brand: 'Roboto', system-ui, sans-serif;
  --md-ref-typeface-plain: 'Roboto', system-ui, sans-serif;
}
#app-slides md-outlined-select, #app-slides md-outlined-text-field { width: 100%; }
#app-slides .autocomplete-wrap { display: block; width: 100%; position: relative; }
#app-slides .filter-row-sort { flex-wrap: wrap; }
#app-slides .filter-row-sort md-outlined-select { width: auto; min-width: 140px; flex: 0 1 auto; }
#app-slides .filter-row-toggle { display: flex; align-items: center; gap: 12px; }
#app-slides .toggle-label {
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-secondary);
}
#app-slides .header-bar md-outlined-select { width: auto; min-width: 220px; }
#app-slides md-assist-chip.chip-level-beginner {
  --md-assist-chip-label-text-color: var(--success);
  --md-assist-chip-outline-color: var(--success);
}
#app-slides md-assist-chip.chip-level-intermediate {
  --md-assist-chip-label-text-color: var(--warning);
  --md-assist-chip-outline-color: var(--warning);
}
#app-slides md-assist-chip.chip-level-advanced {
  --md-assist-chip-label-text-color: var(--danger);
  --md-assist-chip-outline-color: var(--danger);
}
#app-slides md-assist-chip.chip-type-course {
  --md-assist-chip-label-text-color: var(--accent);
  --md-assist-chip-outline-color: var(--accent);
}
#app-slides md-assist-chip.chip-type-lecture {
  --md-assist-chip-label-text-color: var(--text-secondary);
  --md-assist-chip-outline-color: var(--border);
}
#app-slides #index-view ul { list-style: none; padding: 0; margin: 0; }
#app-slides #index-view li a { color: var(--text-primary); font-weight: 500; }
#app-slides #index-view li a:hover { color: var(--accent); text-decoration: none; }
#app-slides body > div > p:last-child, #app-slides #index-view > p:last-child {
  color: var(--text-muted);
  font-size: 0.82rem;
}
#app-slides body > div > p:last-child a, #app-slides #index-view > p:last-child a {
  color: var(--accent);
  text-decoration: none;
}
#app-slides body > div > p:last-child a:hover, #app-slides #index-view > p:last-child a:hover {
  text-decoration: underline;
}
</style>

<div id="app-slides" class="app-root">
<div id="index-view">
<div class="header-bar">
<h1>Course &amp; Lecture Browser</h1>

</div>
<p id="total-count">185 items</p>

<div id="breadcrumb"></div>
<div id="subfolders"></div>

<div class="filters">
<div class="filter-row filter-row-search">
<div class="autocomplete-wrap">
<md-outlined-text-field id="search" label="Search" placeholder="Type to filter by name..." autocomplete="off"></md-outlined-text-field>
<div id="autocomplete-list" class="autocomplete-list"></div>
</div>
</div>
<div class="filter-row">
<md-outlined-select id="filter-level" label="Level">
<md-select-option value="" selected><div slot="headline">All levels</div></md-select-option>
<md-select-option value="advanced"><div slot="headline">advanced</div></md-select-option>
<md-select-option value="beginner"><div slot="headline">beginner</div></md-select-option>
<md-select-option value="intermediate"><div slot="headline">intermediate</div></md-select-option>
</md-outlined-select>
</div>
<div class="filter-row">
<md-outlined-select id="filter-category" label="Category">
<md-select-option value="" selected><div slot="headline">All categories</div></md-select-option>
<md-select-option value="ai"><div slot="headline">ai</div></md-select-option>
<md-select-option value="architecting"><div slot="headline">architecting</div></md-select-option>
<md-select-option value="architecture"><div slot="headline">architecture</div></md-select-option>
<md-select-option value="big-data"><div slot="headline">big-data</div></md-select-option>
<md-select-option value="build-system"><div slot="headline">build-system</div></md-select-option>
<md-select-option value="build-systems"><div slot="headline">build-systems</div></md-select-option>
<md-select-option value="cloud"><div slot="headline">cloud</div></md-select-option>
<md-select-option value="containers"><div slot="headline">containers</div></md-select-option>
<md-select-option value="data-driven"><div slot="headline">data-driven</div></md-select-option>
<md-select-option value="data-engineering"><div slot="headline">data-engineering</div></md-select-option>
<md-select-option value="data-science"><div slot="headline">data-science</div></md-select-option>
<md-select-option value="database"><div slot="headline">database</div></md-select-option>
<md-select-option value="databases"><div slot="headline">databases</div></md-select-option>
<md-select-option value="design-patterns"><div slot="headline">design-patterns</div></md-select-option>
<md-select-option value="devops"><div slot="headline">devops</div></md-select-option>
<md-select-option value="embedded"><div slot="headline">embedded</div></md-select-option>
<md-select-option value="game-development"><div slot="headline">game-development</div></md-select-option>
<md-select-option value="hardware"><div slot="headline">hardware</div></md-select-option>
<md-select-option value="language"><div slot="headline">language</div></md-select-option>
<md-select-option value="machine-learning"><div slot="headline">machine-learning</div></md-select-option>
<md-select-option value="math"><div slot="headline">math</div></md-select-option>
<md-select-option value="message-queue"><div slot="headline">message-queue</div></md-select-option>
<md-select-option value="methodology"><div slot="headline">methodology</div></md-select-option>
<md-select-option value="mobile"><div slot="headline">mobile</div></md-select-option>
<md-select-option value="networking"><div slot="headline">networking</div></md-select-option>
<md-select-option value="observability"><div slot="headline">observability</div></md-select-option>
<md-select-option value="observability-and-monitoring"><div slot="headline">observability-and-monitoring</div></md-select-option>
<md-select-option value="operating-systems"><div slot="headline">operating-systems</div></md-select-option>
<md-select-option value="practices"><div slot="headline">practices</div></md-select-option>
<md-select-option value="real-time"><div slot="headline">real-time</div></md-select-option>
<md-select-option value="security"><div slot="headline">security</div></md-select-option>
<md-select-option value="testing"><div slot="headline">testing</div></md-select-option>
<md-select-option value="version-control"><div slot="headline">version-control</div></md-select-option>
</md-outlined-select>
</div>
<div class="filter-row">
<md-outlined-select id="filter-type" label="Type">
<md-select-option value="" selected><div slot="headline">All types</div></md-select-option>
<md-select-option value="course"><div slot="headline">course</div></md-select-option>
<md-select-option value="lecture"><div slot="headline">lecture</div></md-select-option>
</md-outlined-select>
</div>
<div class="filter-row">
<md-outlined-select id="filter-tag" label="Tag">
<md-select-option value="" selected><div slot="headline">All tags</div></md-select-option>
<md-select-option value="architecting:patterns"><div slot="headline">architecting:patterns</div></md-select-option>
<md-select-option value="architecture:api"><div slot="headline">architecture:api</div></md-select-option>
<md-select-option value="architecture:api-gateway"><div slot="headline">architecture:api-gateway</div></md-select-option>
<md-select-option value="architecture:clean-architecture"><div slot="headline">architecture:clean-architecture</div></md-select-option>
<md-select-option value="architecture:cqrs"><div slot="headline">architecture:cqrs</div></md-select-option>
<md-select-option value="architecture:distributed-systems"><div slot="headline">architecture:distributed-systems</div></md-select-option>
<md-select-option value="architecture:distributed-transactions"><div slot="headline">architecture:distributed-transactions</div></md-select-option>
<md-select-option value="architecture:event-sourcing"><div slot="headline">architecture:event-sourcing</div></md-select-option>
<md-select-option value="architecture:hexagonal"><div slot="headline">architecture:hexagonal</div></md-select-option>
<md-select-option value="architecture:microservices"><div slot="headline">architecture:microservices</div></md-select-option>
<md-select-option value="architecture:openapi"><div slot="headline">architecture:openapi</div></md-select-option>
<md-select-option value="architecture:saga"><div slot="headline">architecture:saga</div></md-select-option>
<md-select-option value="architecture:serverless"><div slot="headline">architecture:serverless</div></md-select-option>
<md-select-option value="architecture:system-design"><div slot="headline">architecture:system-design</div></md-select-option>
<md-select-option value="audiences:devops"><div slot="headline">audiences:devops</div></md-select-option>
<md-select-option value="audiences:sysadmin"><div slot="headline">audiences:sysadmin</div></md-select-option>
<md-select-option value="concepts:agents"><div slot="headline">concepts:agents</div></md-select-option>
<md-select-option value="concepts:ai"><div slot="headline">concepts:ai</div></md-select-option>
<md-select-option value="concepts:algorithms"><div slot="headline">concepts:algorithms</div></md-select-option>
<md-select-option value="concepts:api"><div slot="headline">concepts:api</div></md-select-option>
<md-select-option value="concepts:api-design"><div slot="headline">concepts:api-design</div></md-select-option>
<md-select-option value="concepts:architecture"><div slot="headline">concepts:architecture</div></md-select-option>
<md-select-option value="concepts:automation"><div slot="headline">concepts:automation</div></md-select-option>
<md-select-option value="concepts:best-practices"><div slot="headline">concepts:best-practices</div></md-select-option>
<md-select-option value="concepts:bootloader"><div slot="headline">concepts:bootloader</div></md-select-option>
<md-select-option value="concepts:bsp"><div slot="headline">concepts:bsp</div></md-select-option>
<md-select-option value="concepts:clean-code"><div slot="headline">concepts:clean-code</div></md-select-option>
<md-select-option value="concepts:cloud-economics"><div slot="headline">concepts:cloud-economics</div></md-select-option>
<md-select-option value="concepts:code-generation"><div slot="headline">concepts:code-generation</div></md-select-option>
<md-select-option value="concepts:code-review"><div slot="headline">concepts:code-review</div></md-select-option>
<md-select-option value="concepts:compilation"><div slot="headline">concepts:compilation</div></md-select-option>
<md-select-option value="concepts:computer-architecture"><div slot="headline">concepts:computer-architecture</div></md-select-option>
<md-select-option value="concepts:concurrency"><div slot="headline">concepts:concurrency</div></md-select-option>
<md-select-option value="concepts:cross-compilation"><div slot="headline">concepts:cross-compilation</div></md-select-option>
<md-select-option value="concepts:data-formats"><div slot="headline">concepts:data-formats</div></md-select-option>
<md-select-option value="concepts:data-integrity"><div slot="headline">concepts:data-integrity</div></md-select-option>
<md-select-option value="concepts:data-modeling"><div slot="headline">concepts:data-modeling</div></md-select-option>
<md-select-option value="concepts:data-science"><div slot="headline">concepts:data-science</div></md-select-option>
<md-select-option value="concepts:data-structures"><div slot="headline">concepts:data-structures</div></md-select-option>
<md-select-option value="concepts:databases"><div slot="headline">concepts:databases</div></md-select-option>
<md-select-option value="concepts:dataframes"><div slot="headline">concepts:dataframes</div></md-select-option>
<md-select-option value="concepts:design-patterns"><div slot="headline">concepts:design-patterns</div></md-select-option>
<md-select-option value="concepts:device-drivers"><div slot="headline">concepts:device-drivers</div></md-select-option>
<md-select-option value="concepts:distributed-systems"><div slot="headline">concepts:distributed-systems</div></md-select-option>
<md-select-option value="concepts:domain-driven-design"><div slot="headline">concepts:domain-driven-design</div></md-select-option>
<md-select-option value="concepts:drivers"><div slot="headline">concepts:drivers</div></md-select-option>
<md-select-option value="concepts:embedded"><div slot="headline">concepts:embedded</div></md-select-option>
<md-select-option value="concepts:embeddings"><div slot="headline">concepts:embeddings</div></md-select-option>
<md-select-option value="concepts:ethics"><div slot="headline">concepts:ethics</div></md-select-option>
<md-select-option value="concepts:eventual-consistency"><div slot="headline">concepts:eventual-consistency</div></md-select-option>
<md-select-option value="concepts:filesystems"><div slot="headline">concepts:filesystems</div></md-select-option>
<md-select-option value="concepts:firmware"><div slot="headline">concepts:firmware</div></md-select-option>
<md-select-option value="concepts:functional-programming"><div slot="headline">concepts:functional-programming</div></md-select-option>
<md-select-option value="concepts:hardware"><div slot="headline">concepts:hardware</div></md-select-option>
<md-select-option value="concepts:idempotency"><div slot="headline">concepts:idempotency</div></md-select-option>
<md-select-option value="concepts:internet-infrastructure"><div slot="headline">concepts:internet-infrastructure</div></md-select-option>
<md-select-option value="concepts:interrupts"><div slot="headline">concepts:interrupts</div></md-select-option>
<md-select-option value="concepts:io"><div slot="headline">concepts:io</div></md-select-option>
<md-select-option value="concepts:isolation"><div slot="headline">concepts:isolation</div></md-select-option>
<md-select-option value="concepts:kernel"><div slot="headline">concepts:kernel</div></md-select-option>
<md-select-option value="concepts:linux-kernel"><div slot="headline">concepts:linux-kernel</div></md-select-option>
<md-select-option value="concepts:llm"><div slot="headline">concepts:llm</div></md-select-option>
<md-select-option value="concepts:mcp"><div slot="headline">concepts:mcp</div></md-select-option>
<md-select-option value="concepts:memory-management"><div slot="headline">concepts:memory-management</div></md-select-option>
<md-select-option value="concepts:microservices"><div slot="headline">concepts:microservices</div></md-select-option>
<md-select-option value="concepts:mobile-development"><div slot="headline">concepts:mobile-development</div></md-select-option>
<md-select-option value="concepts:multithreading"><div slot="headline">concepts:multithreading</div></md-select-option>
<md-select-option value="concepts:networking"><div slot="headline">concepts:networking</div></md-select-option>
<md-select-option value="concepts:numerical-computing"><div slot="headline">concepts:numerical-computing</div></md-select-option>
<md-select-option value="concepts:oop"><div slot="headline">concepts:oop</div></md-select-option>
<md-select-option value="concepts:orchestration"><div slot="headline">concepts:orchestration</div></md-select-option>
<md-select-option value="concepts:performance"><div slot="headline">concepts:performance</div></md-select-option>
<md-select-option value="concepts:pointers"><div slot="headline">concepts:pointers</div></md-select-option>
<md-select-option value="concepts:programming"><div slot="headline">concepts:programming</div></md-select-option>
<md-select-option value="concepts:prompting"><div slot="headline">concepts:prompting</div></md-select-option>
<md-select-option value="concepts:protocols"><div slot="headline">concepts:protocols</div></md-select-option>
<md-select-option value="concepts:reliability"><div slot="headline">concepts:reliability</div></md-select-option>
<md-select-option value="concepts:rest"><div slot="headline">concepts:rest</div></md-select-option>
<md-select-option value="concepts:scalability"><div slot="headline">concepts:scalability</div></md-select-option>
<md-select-option value="concepts:security"><div slot="headline">concepts:security</div></md-select-option>
<md-select-option value="concepts:serialization"><div slot="headline">concepts:serialization</div></md-select-option>
<md-select-option value="concepts:service-mesh"><div slot="headline">concepts:service-mesh</div></md-select-option>
<md-select-option value="concepts:solid"><div slot="headline">concepts:solid</div></md-select-option>
<md-select-option value="concepts:systems-programming"><div slot="headline">concepts:systems-programming</div></md-select-option>
<md-select-option value="concepts:tools"><div slot="headline">concepts:tools</div></md-select-option>
<md-select-option value="concepts:transactions"><div slot="headline">concepts:transactions</div></md-select-option>
<md-select-option value="concepts:version-control"><div slot="headline">concepts:version-control</div></md-select-option>
<md-select-option value="concepts:virtualization"><div slot="headline">concepts:virtualization</div></md-select-option>
<md-select-option value="concepts:workflows"><div slot="headline">concepts:workflows</div></md-select-option>
<md-select-option value="data-and-ai:agents"><div slot="headline">data-and-ai:agents</div></md-select-option>
<md-select-option value="data-and-ai:ai"><div slot="headline">data-and-ai:ai</div></md-select-option>
<md-select-option value="data-and-ai:airflow"><div slot="headline">data-and-ai:airflow</div></md-select-option>
<md-select-option value="data-and-ai:big-data"><div slot="headline">data-and-ai:big-data</div></md-select-option>
<md-select-option value="data-and-ai:business-intelligence"><div slot="headline">data-and-ai:business-intelligence</div></md-select-option>
<md-select-option value="data-and-ai:caching"><div slot="headline">data-and-ai:caching</div></md-select-option>
<md-select-option value="data-and-ai:data-analysis"><div slot="headline">data-and-ai:data-analysis</div></md-select-option>
<md-select-option value="data-and-ai:data-analytics"><div slot="headline">data-and-ai:data-analytics</div></md-select-option>
<md-select-option value="data-and-ai:data-engineering"><div slot="headline">data-and-ai:data-engineering</div></md-select-option>
<md-select-option value="data-and-ai:dbt"><div slot="headline">data-and-ai:dbt</div></md-select-option>
<md-select-option value="data-and-ai:deep-learning"><div slot="headline">data-and-ai:deep-learning</div></md-select-option>
<md-select-option value="data-and-ai:generative-ai"><div slot="headline">data-and-ai:generative-ai</div></md-select-option>
<md-select-option value="data-and-ai:llm"><div slot="headline">data-and-ai:llm</div></md-select-option>
<md-select-option value="data-and-ai:machine-learning"><div slot="headline">data-and-ai:machine-learning</div></md-select-option>
<md-select-option value="data-and-ai:mcp"><div slot="headline">data-and-ai:mcp</div></md-select-option>
<md-select-option value="data-and-ai:message-queues"><div slot="headline">data-and-ai:message-queues</div></md-select-option>
<md-select-option value="data-and-ai:ml"><div slot="headline">data-and-ai:ml</div></md-select-option>
<md-select-option value="data-and-ai:nlp"><div slot="headline">data-and-ai:nlp</div></md-select-option>
<md-select-option value="data-and-ai:nosql"><div slot="headline">data-and-ai:nosql</div></md-select-option>
<md-select-option value="data-and-ai:orchestration"><div slot="headline">data-and-ai:orchestration</div></md-select-option>
<md-select-option value="data-and-ai:prompt-engineering"><div slot="headline">data-and-ai:prompt-engineering</div></md-select-option>
<md-select-option value="data-and-ai:rag"><div slot="headline">data-and-ai:rag</div></md-select-option>
<md-select-option value="data-and-ai:search"><div slot="headline">data-and-ai:search</div></md-select-option>
<md-select-option value="data-and-ai:statistics"><div slot="headline">data-and-ai:statistics</div></md-select-option>
<md-select-option value="data-and-ai:streaming"><div slot="headline">data-and-ai:streaming</div></md-select-option>
<md-select-option value="data-and-ai:transformation"><div slot="headline">data-and-ai:transformation</div></md-select-option>
<md-select-option value="databases:cassandra"><div slot="headline">databases:cassandra</div></md-select-option>
<md-select-option value="databases:clickhouse"><div slot="headline">databases:clickhouse</div></md-select-option>
<md-select-option value="databases:cockroachdb"><div slot="headline">databases:cockroachdb</div></md-select-option>
<md-select-option value="databases:design"><div slot="headline">databases:design</div></md-select-option>
<md-select-option value="databases:duckdb"><div slot="headline">databases:duckdb</div></md-select-option>
<md-select-option value="databases:dynamodb"><div slot="headline">databases:dynamodb</div></md-select-option>
<md-select-option value="databases:elasticsearch"><div slot="headline">databases:elasticsearch</div></md-select-option>
<md-select-option value="databases:migrations"><div slot="headline">databases:migrations</div></md-select-option>
<md-select-option value="databases:mongodb"><div slot="headline">databases:mongodb</div></md-select-option>
<md-select-option value="databases:neo4j"><div slot="headline">databases:neo4j</div></md-select-option>
<md-select-option value="databases:nosql"><div slot="headline">databases:nosql</div></md-select-option>
<md-select-option value="databases:postgresql"><div slot="headline">databases:postgresql</div></md-select-option>
<md-select-option value="databases:relational"><div slot="headline">databases:relational</div></md-select-option>
<md-select-option value="databases:sql"><div slot="headline">databases:sql</div></md-select-option>
<md-select-option value="hardware-and-embedded:embedded"><div slot="headline">hardware-and-embedded:embedded</div></md-select-option>
<md-select-option value="hardware-and-embedded:hardware-programming"><div slot="headline">hardware-and-embedded:hardware-programming</div></md-select-option>
<md-select-option value="hardware-and-embedded:x86"><div slot="headline">hardware-and-embedded:x86</div></md-select-option>
<md-select-option value="infrastructure:android"><div slot="headline">infrastructure:android</div></md-select-option>
<md-select-option value="infrastructure:aws"><div slot="headline">infrastructure:aws</div></md-select-option>
<md-select-option value="infrastructure:azure"><div slot="headline">infrastructure:azure</div></md-select-option>
<md-select-option value="infrastructure:cloud"><div slot="headline">infrastructure:cloud</div></md-select-option>
<md-select-option value="infrastructure:cloud-native"><div slot="headline">infrastructure:cloud-native</div></md-select-option>
<md-select-option value="infrastructure:configuration-management"><div slot="headline">infrastructure:configuration-management</div></md-select-option>
<md-select-option value="infrastructure:containers"><div slot="headline">infrastructure:containers</div></md-select-option>
<md-select-option value="infrastructure:docker"><div slot="headline">infrastructure:docker</div></md-select-option>
<md-select-option value="infrastructure:embedded"><div slot="headline">infrastructure:embedded</div></md-select-option>
<md-select-option value="infrastructure:gcp"><div slot="headline">infrastructure:gcp</div></md-select-option>
<md-select-option value="infrastructure:grafana"><div slot="headline">infrastructure:grafana</div></md-select-option>
<md-select-option value="infrastructure:iaas"><div slot="headline">infrastructure:iaas</div></md-select-option>
<md-select-option value="infrastructure:infrastructure-as-code"><div slot="headline">infrastructure:infrastructure-as-code</div></md-select-option>
<md-select-option value="infrastructure:io"><div slot="headline">infrastructure:io</div></md-select-option>
<md-select-option value="infrastructure:ipc"><div slot="headline">infrastructure:ipc</div></md-select-option>
<md-select-option value="infrastructure:k8s"><div slot="headline">infrastructure:k8s</div></md-select-option>
<md-select-option value="infrastructure:kubernetes"><div slot="headline">infrastructure:kubernetes</div></md-select-option>
<md-select-option value="infrastructure:linux"><div slot="headline">infrastructure:linux</div></md-select-option>
<md-select-option value="infrastructure:low-level"><div slot="headline">infrastructure:low-level</div></md-select-option>
<md-select-option value="infrastructure:networking"><div slot="headline">infrastructure:networking</div></md-select-option>
<md-select-option value="infrastructure:onprem"><div slot="headline">infrastructure:onprem</div></md-select-option>
<md-select-option value="infrastructure:opentelemetry"><div slot="headline">infrastructure:opentelemetry</div></md-select-option>
<md-select-option value="infrastructure:orchestration"><div slot="headline">infrastructure:orchestration</div></md-select-option>
<md-select-option value="infrastructure:paas"><div slot="headline">infrastructure:paas</div></md-select-option>
<md-select-option value="infrastructure:prometheus"><div slot="headline">infrastructure:prometheus</div></md-select-option>
<md-select-option value="infrastructure:real-time"><div slot="headline">infrastructure:real-time</div></md-select-option>
<md-select-option value="infrastructure:storage"><div slot="headline">infrastructure:storage</div></md-select-option>
<md-select-option value="infrastructure:unix"><div slot="headline">infrastructure:unix</div></md-select-option>
<md-select-option value="infrastructure:virtualization"><div slot="headline">infrastructure:virtualization</div></md-select-option>
<md-select-option value="languages:assembly"><div slot="headline">languages:assembly</div></md-select-option>
<md-select-option value="languages:bash"><div slot="headline">languages:bash</div></md-select-option>
<md-select-option value="languages:c"><div slot="headline">languages:c</div></md-select-option>
<md-select-option value="languages:c++"><div slot="headline">languages:c++</div></md-select-option>
<md-select-option value="languages:c++11"><div slot="headline">languages:c++11</div></md-select-option>
<md-select-option value="languages:c++17"><div slot="headline">languages:c++17</div></md-select-option>
<md-select-option value="languages:cpp"><div slot="headline">languages:cpp</div></md-select-option>
<md-select-option value="languages:go"><div slot="headline">languages:go</div></md-select-option>
<md-select-option value="languages:java"><div slot="headline">languages:java</div></md-select-option>
<md-select-option value="languages:python"><div slot="headline">languages:python</div></md-select-option>
<md-select-option value="languages:r"><div slot="headline">languages:r</div></md-select-option>
<md-select-option value="languages:rust"><div slot="headline">languages:rust</div></md-select-option>
<md-select-option value="languages:scala"><div slot="headline">languages:scala</div></md-select-option>
<md-select-option value="languages:shell"><div slot="headline">languages:shell</div></md-select-option>
<md-select-option value="languages:sql"><div slot="headline">languages:sql</div></md-select-option>
<md-select-option value="math:descriptive-statistics"><div slot="headline">math:descriptive-statistics</div></md-select-option>
<md-select-option value="math:estimation"><div slot="headline">math:estimation</div></md-select-option>
<md-select-option value="math:hypothesis-testing"><div slot="headline">math:hypothesis-testing</div></md-select-option>
<md-select-option value="math:inferential-statistics"><div slot="headline">math:inferential-statistics</div></md-select-option>
<md-select-option value="math:probability"><div slot="headline">math:probability</div></md-select-option>
<md-select-option value="math:regression"><div slot="headline">math:regression</div></md-select-option>
<md-select-option value="math:statistics"><div slot="headline">math:statistics</div></md-select-option>
<md-select-option value="networking:802.11"><div slot="headline">networking:802.11</div></md-select-option>
<md-select-option value="networking:api"><div slot="headline">networking:api</div></md-select-option>
<md-select-option value="networking:dns"><div slot="headline">networking:dns</div></md-select-option>
<md-select-option value="networking:graphql"><div slot="headline">networking:graphql</div></md-select-option>
<md-select-option value="networking:grpc"><div slot="headline">networking:grpc</div></md-select-option>
<md-select-option value="networking:http"><div slot="headline">networking:http</div></md-select-option>
<md-select-option value="networking:networking"><div slot="headline">networking:networking</div></md-select-option>
<md-select-option value="networking:protocols"><div slot="headline">networking:protocols</div></md-select-option>
<md-select-option value="networking:rest"><div slot="headline">networking:rest</div></md-select-option>
<md-select-option value="networking:tcp-ip"><div slot="headline">networking:tcp-ip</div></md-select-option>
<md-select-option value="networking:wifi"><div slot="headline">networking:wifi</div></md-select-option>
<md-select-option value="observability:grafana"><div slot="headline">observability:grafana</div></md-select-option>
<md-select-option value="observability:tracing"><div slot="headline">observability:tracing</div></md-select-option>
<md-select-option value="practices:agile"><div slot="headline">practices:agile</div></md-select-option>
<md-select-option value="practices:api"><div slot="headline">practices:api</div></md-select-option>
<md-select-option value="practices:automation"><div slot="headline">practices:automation</div></md-select-option>
<md-select-option value="practices:build-systems"><div slot="headline">practices:build-systems</div></md-select-option>
<md-select-option value="practices:ci-cd"><div slot="headline">practices:ci-cd</div></md-select-option>
<md-select-option value="practices:code-quality"><div slot="headline">practices:code-quality</div></md-select-option>
<md-select-option value="practices:collaboration"><div slot="headline">practices:collaboration</div></md-select-option>
<md-select-option value="practices:command-line"><div slot="headline">practices:command-line</div></md-select-option>
<md-select-option value="practices:containers"><div slot="headline">practices:containers</div></md-select-option>
<md-select-option value="practices:cost-optimization"><div slot="headline">practices:cost-optimization</div></md-select-option>
<md-select-option value="practices:ddd"><div slot="headline">practices:ddd</div></md-select-option>
<md-select-option value="practices:debugging"><div slot="headline">practices:debugging</div></md-select-option>
<md-select-option value="practices:design"><div slot="headline">practices:design</div></md-select-option>
<md-select-option value="practices:devops"><div slot="headline">practices:devops</div></md-select-option>
<md-select-option value="practices:finops"><div slot="headline">practices:finops</div></md-select-option>
<md-select-option value="practices:game-development"><div slot="headline">practices:game-development</div></md-select-option>
<md-select-option value="practices:large-codebases"><div slot="headline">practices:large-codebases</div></md-select-option>
<md-select-option value="practices:leadership"><div slot="headline">practices:leadership</div></md-select-option>
<md-select-option value="practices:logging"><div slot="headline">practices:logging</div></md-select-option>
<md-select-option value="practices:methodology"><div slot="headline">practices:methodology</div></md-select-option>
<md-select-option value="practices:migration"><div slot="headline">practices:migration</div></md-select-option>
<md-select-option value="practices:monitoring"><div slot="headline">practices:monitoring</div></md-select-option>
<md-select-option value="practices:observability"><div slot="headline">practices:observability</div></md-select-option>
<md-select-option value="practices:performance"><div slot="headline">practices:performance</div></md-select-option>
<md-select-option value="practices:productivity"><div slot="headline">practices:productivity</div></md-select-option>
<md-select-option value="practices:project-management"><div slot="headline">practices:project-management</div></md-select-option>
<md-select-option value="practices:refactoring"><div slot="headline">practices:refactoring</div></md-select-option>
<md-select-option value="practices:reliability"><div slot="headline">practices:reliability</div></md-select-option>
<md-select-option value="practices:scalability"><div slot="headline">practices:scalability</div></md-select-option>
<md-select-option value="practices:scripting"><div slot="headline">practices:scripting</div></md-select-option>
<md-select-option value="practices:scrum"><div slot="headline">practices:scrum</div></md-select-option>
<md-select-option value="practices:serverless"><div slot="headline">practices:serverless</div></md-select-option>
<md-select-option value="practices:software-design"><div slot="headline">practices:software-design</div></md-select-option>
<md-select-option value="practices:sre"><div slot="headline">practices:sre</div></md-select-option>
<md-select-option value="practices:tdd"><div slot="headline">practices:tdd</div></md-select-option>
<md-select-option value="practices:testing"><div slot="headline">practices:testing</div></md-select-option>
<md-select-option value="practices:tools"><div slot="headline">practices:tools</div></md-select-option>
<md-select-option value="protocols:dns"><div slot="headline">protocols:dns</div></md-select-option>
<md-select-option value="queues:overview"><div slot="headline">queues:overview</div></md-select-option>
<md-select-option value="security:application-security"><div slot="headline">security:application-security</div></md-select-option>
<md-select-option value="security:authentication"><div slot="headline">security:authentication</div></md-select-option>
<md-select-option value="security:authorization"><div slot="headline">security:authorization</div></md-select-option>
<md-select-option value="security:cloud-native"><div slot="headline">security:cloud-native</div></md-select-option>
<md-select-option value="security:compliance"><div slot="headline">security:compliance</div></md-select-option>
<md-select-option value="security:cryptography"><div slot="headline">security:cryptography</div></md-select-option>
<md-select-option value="security:cyber-attacks"><div slot="headline">security:cyber-attacks</div></md-select-option>
<md-select-option value="security:encryption"><div slot="headline">security:encryption</div></md-select-option>
<md-select-option value="security:forensics"><div slot="headline">security:forensics</div></md-select-option>
<md-select-option value="security:kubernetes"><div slot="headline">security:kubernetes</div></md-select-option>
<md-select-option value="security:network"><div slot="headline">security:network</div></md-select-option>
<md-select-option value="security:owasp"><div slot="headline">security:owasp</div></md-select-option>
<md-select-option value="security:penetration-testing"><div slot="headline">security:penetration-testing</div></md-select-option>
<md-select-option value="security:policies"><div slot="headline">security:policies</div></md-select-option>
<md-select-option value="security:secure-coding"><div slot="headline">security:secure-coding</div></md-select-option>
<md-select-option value="security:security"><div slot="headline">security:security</div></md-select-option>
<md-select-option value="security:tls"><div slot="headline">security:tls</div></md-select-option>
<md-select-option value="security:vulnerabilities"><div slot="headline">security:vulnerabilities</div></md-select-option>
<md-select-option value="security:web-security"><div slot="headline">security:web-security</div></md-select-option>
<md-select-option value="testing:chaos"><div slot="headline">testing:chaos</div></md-select-option>
<md-select-option value="testing:contract"><div slot="headline">testing:contract</div></md-select-option>
<md-select-option value="testing:performance"><div slot="headline">testing:performance</div></md-select-option>
<md-select-option value="tools:ansible"><div slot="headline">tools:ansible</div></md-select-option>
<md-select-option value="tools:azure"><div slot="headline">tools:azure</div></md-select-option>
<md-select-option value="tools:cmake"><div slot="headline">tools:cmake</div></md-select-option>
<md-select-option value="tools:docker"><div slot="headline">tools:docker</div></md-select-option>
<md-select-option value="tools:elk"><div slot="headline">tools:elk</div></md-select-option>
<md-select-option value="tools:gcc"><div slot="headline">tools:gcc</div></md-select-option>
<md-select-option value="tools:git"><div slot="headline">tools:git</div></md-select-option>
<md-select-option value="tools:github"><div slot="headline">tools:github</div></md-select-option>
<md-select-option value="tools:jupyter"><div slot="headline">tools:jupyter</div></md-select-option>
<md-select-option value="tools:kafka"><div slot="headline">tools:kafka</div></md-select-option>
<md-select-option value="tools:kubernetes"><div slot="headline">tools:kubernetes</div></md-select-option>
<md-select-option value="tools:logstash"><div slot="headline">tools:logstash</div></md-select-option>
<md-select-option value="tools:make"><div slot="headline">tools:make</div></md-select-option>
<md-select-option value="tools:numpy"><div slot="headline">tools:numpy</div></md-select-option>
<md-select-option value="tools:pandas"><div slot="headline">tools:pandas</div></md-select-option>
<md-select-option value="tools:polars"><div slot="headline">tools:polars</div></md-select-option>
<md-select-option value="tools:pytorch"><div slot="headline">tools:pytorch</div></md-select-option>
<md-select-option value="tools:qemu"><div slot="headline">tools:qemu</div></md-select-option>
<md-select-option value="tools:rabbitmq"><div slot="headline">tools:rabbitmq</div></md-select-option>
<md-select-option value="tools:redis"><div slot="headline">tools:redis</div></md-select-option>
<md-select-option value="tools:spark"><div slot="headline">tools:spark</div></md-select-option>
<md-select-option value="tools:tensorflow"><div slot="headline">tools:tensorflow</div></md-select-option>
<md-select-option value="tools:terraform"><div slot="headline">tools:terraform</div></md-select-option>
<md-select-option value="tools:terragrunt"><div slot="headline">tools:terragrunt</div></md-select-option>
<md-select-option value="tools:unity"><div slot="headline">tools:unity</div></md-select-option>
<md-select-option value="tools:yocto"><div slot="headline">tools:yocto</div></md-select-option>
</md-outlined-select>
</div>
<div class="filter-row">
<md-outlined-select id="filter-duration" label="Duration"></md-outlined-select>
</div>
<div class="filter-row">
<md-outlined-select id="filter-audience" label="Audience">
<md-select-option value="" selected><div slot="headline">All audiences</div></md-select-option>
<md-select-option value="audiences:analysts"><div slot="headline">audiences:analysts</div></md-select-option>
<md-select-option value="audiences:architects"><div slot="headline">audiences:architects</div></md-select-option>
<md-select-option value="audiences:data-analysts"><div slot="headline">audiences:data-analysts</div></md-select-option>
<md-select-option value="audiences:data-engineers"><div slot="headline">audiences:data-engineers</div></md-select-option>
<md-select-option value="audiences:data-scientists"><div slot="headline">audiences:data-scientists</div></md-select-option>
<md-select-option value="audiences:dba"><div slot="headline">audiences:dba</div></md-select-option>
<md-select-option value="audiences:dbas"><div slot="headline">audiences:dbas</div></md-select-option>
<md-select-option value="audiences:developers"><div slot="headline">audiences:developers</div></md-select-option>
<md-select-option value="audiences:devops"><div slot="headline">audiences:devops</div></md-select-option>
<md-select-option value="audiences:embedded-engineers"><div slot="headline">audiences:embedded-engineers</div></md-select-option>
<md-select-option value="audiences:managers"><div slot="headline">audiences:managers</div></md-select-option>
<md-select-option value="audiences:ml-engineers"><div slot="headline">audiences:ml-engineers</div></md-select-option>
<md-select-option value="audiences:network-engineers"><div slot="headline">audiences:network-engineers</div></md-select-option>
<md-select-option value="audiences:security"><div slot="headline">audiences:security</div></md-select-option>
<md-select-option value="audiences:security-professionals"><div slot="headline">audiences:security-professionals</div></md-select-option>
<md-select-option value="audiences:senior-developers"><div slot="headline">audiences:senior-developers</div></md-select-option>
<md-select-option value="audiences:sysadmins"><div slot="headline">audiences:sysadmins</div></md-select-option>
<md-select-option value="audiences:team-leads"><div slot="headline">audiences:team-leads</div></md-select-option>
<md-select-option value="audiences:testers"><div slot="headline">audiences:testers</div></md-select-option>
</md-outlined-select>
</div>
<div class="filter-row filter-row-toggle">
<label for="show-numbers" class="toggle-label">Numbering</label>
<md-switch id="show-numbers"></md-switch>
</div>
<div class="filter-row filter-row-sort">
<md-outlined-select id="sort-primary" label="Sort by">
<md-select-option value="folder" selected><div slot="headline">Folder</div></md-select-option>
<md-select-option value="name"><div slot="headline">Name</div></md-select-option>
<md-select-option value="level"><div slot="headline">Level</div></md-select-option>
<md-select-option value="category"><div slot="headline">Category</div></md-select-option>
<md-select-option value="duration"><div slot="headline">Duration</div></md-select-option>
<md-select-option value="slides"><div slot="headline">Slides</div></md-select-option>
<md-select-option value="chapters"><div slot="headline">Chapters</div></md-select-option>
</md-outlined-select>
<md-outlined-select id="sort-primary-dir" label="Direction">
<md-select-option value="asc" selected><div slot="headline">Asc</div></md-select-option>
<md-select-option value="desc"><div slot="headline">Desc</div></md-select-option>
</md-outlined-select>
<md-outlined-select id="sort-secondary" label="Then by">
<md-select-option value="name" selected><div slot="headline">Name</div></md-select-option>
<md-select-option value="folder"><div slot="headline">Folder</div></md-select-option>
<md-select-option value="level"><div slot="headline">Level</div></md-select-option>
<md-select-option value="category"><div slot="headline">Category</div></md-select-option>
<md-select-option value="duration"><div slot="headline">Duration</div></md-select-option>
<md-select-option value="slides"><div slot="headline">Slides</div></md-select-option>
<md-select-option value="chapters"><div slot="headline">Chapters</div></md-select-option>
</md-outlined-select>
<md-outlined-select id="sort-secondary-dir" label="Direction">
<md-select-option value="asc" selected><div slot="headline">Asc</div></md-select-option>
<md-select-option value="desc"><div slot="headline">Desc</div></md-select-option>
</md-outlined-select>
</div>
</div>

<div id="results"></div>

<hr>
<p>Mark Veltzer <a href="mailto:mark.veltzer@gmail.com">mark.veltzer@gmail.com</a> <a href="https://github.com/veltzer">@veltzer</a></p>
<p class="build-info">Built from <code>3afbe1e3f8f0</code> on 2026-08-27 12:37 UTC &middot; local build</p>
</div>
</div>

<script type="module">
import "https://cdn.jsdelivr.net/npm/@material/web@2/all.js/+esm";
window.__mdReady = Promise.all([
  customElements.whenDefined("md-outlined-text-field"),
  customElements.whenDefined("md-outlined-select"),
  customElements.whenDefined("md-select-option"),
  customElements.whenDefined("md-assist-chip"),
  customElements.whenDefined("md-switch"),
]);
</script>

<script>
const DATA = [{"name": "Advanced Ai Powered Development", "type": "course", "chapters": 12, "slides": 407, "folder": "courses/ai/advanced-ai-powered-development", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/advanced-ai-powered-development.pdf", "level": "advanced", "category": "ai", "duration_hours": 40, "tags": ["data-and-ai:ai", "data-and-ai:agents", "data-and-ai:mcp", "data-and-ai:rag", "practices:tools", "practices:large-codebases", "data-and-ai:prompt-engineering", "practices:productivity"], "audience": ["audiences:developers", "audiences:architects", "audiences:team-leads", "audiences:devops"]}, {"name": "Ai Agents Development", "type": "course", "chapters": 6, "slides": 79, "folder": "courses/ai/ai-agents-development", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/ai-agents-development.pdf", "level": "advanced", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:llm"], "audience": ["audiences:developers"]}, {"name": "Claude Workshop", "type": "course", "chapters": 9, "slides": 211, "folder": "courses/ai/claude-workshop", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/claude-workshop.pdf", "level": "intermediate", "category": "ai", "duration_hours": 8, "tags": ["data-and-ai:ai", "data-and-ai:llm", "data-and-ai:agents", "data-and-ai:mcp", "data-and-ai:rag", "data-and-ai:prompt-engineering", "practices:productivity"], "audience": ["audiences:developers", "audiences:senior-developers", "audiences:devops"]}, {"name": "Developing Using Ai", "type": "course", "chapters": 15, "slides": 737, "folder": "courses/ai/developing-using-ai", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/developing-using-ai.pdf", "level": "intermediate", "category": "ai", "duration_hours": 24, "tags": ["data-and-ai:ai", "concepts:code-generation", "data-and-ai:prompt-engineering", "practices:productivity"], "audience": ["audiences:developers"]}, {"name": "Generative Ai Applications", "type": "course", "chapters": 21, "slides": 569, "folder": "courses/ai/generative-ai-applications", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/generative-ai-applications.pdf", "level": "intermediate", "category": "ai", "duration_hours": 40, "tags": ["data-and-ai:ai", "data-and-ai:generative-ai", "languages:python", "data-and-ai:prompt-engineering", "concepts:ethics"], "audience": ["audiences:data-scientists"]}, {"name": "Mlops", "type": "course", "chapters": 6, "slides": 83, "folder": "courses/ai/mlops", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/mlops.pdf", "level": "advanced", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:machine-learning", "practices:devops"], "audience": ["audiences:data-scientists", "audiences:devops"]}, {"name": "Natural Language Processing", "type": "course", "chapters": 27, "slides": 903, "folder": "courses/ai/natural-language-processing", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/natural-language-processing.pdf", "level": "advanced", "category": "ai", "duration_hours": 64, "tags": ["data-and-ai:nlp", "data-and-ai:machine-learning", "data-and-ai:deep-learning", "data-and-ai:llm", "concepts:embeddings"], "audience": ["audiences:developers", "audiences:data-scientists", "audiences:architects"]}, {"name": "Nlp With Python", "type": "course", "chapters": 6, "slides": 80, "folder": "courses/ai/nlp-with-python", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/nlp-with-python.pdf", "level": "intermediate", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:nlp", "languages:python"], "audience": ["audiences:data-scientists"]}, {"name": "Prompt Engineering", "type": "course", "chapters": 6, "slides": 80, "folder": "courses/ai/prompt-engineering", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/prompt-engineering.pdf", "level": "intermediate", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:llm"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Rag Applications", "type": "course", "chapters": 6, "slides": 84, "folder": "courses/ai/rag-applications", "folder_label": "Ai", "pdf": "/teaching-slides/pdfunite/ai/rag-applications.pdf", "level": "intermediate", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:llm"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Api Design Best Practices", "type": "course", "chapters": 13, "slides": 226, "folder": "courses/architecting/api-design-best-practices", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/api-design-best-practices.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["concepts:api", "concepts:rest", "concepts:architecture", "concepts:best-practices"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Api First Development", "type": "course", "chapters": 9, "slides": 154, "folder": "courses/architecting/api-first-development", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/api-first-development.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["architecture:api", "architecture:openapi", "practices:design"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Api Gateway Patterns", "type": "course", "chapters": 11, "slides": 178, "folder": "courses/architecting/api-gateway-patterns", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/api-gateway-patterns.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["architecture:api-gateway", "architecture:microservices"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Architecting", "type": "course", "chapters": 20, "slides": 646, "folder": "courses/architecting/architecting", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/architecting.pdf", "level": "advanced", "category": "architecture", "duration_hours": 40, "tags": ["concepts:architecture", "concepts:microservices", "infrastructure:cloud-native", "concepts:domain-driven-design", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:architects", "audiences:devops"]}, {"name": "Architecture Patterns", "type": "course", "chapters": 18, "slides": 526, "folder": "courses/architecting/architecture-patterns", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/architecture-patterns.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 40, "tags": ["concepts:architecture", "concepts:microservices", "infrastructure:cloud", "practices:ci-cd", "concepts:design-patterns"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Clean And Hexagonal Architecture", "type": "course", "chapters": 9, "slides": 137, "folder": "courses/architecting/clean-and-hexagonal-architecture", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/clean-and-hexagonal-architecture.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["architecture:clean-architecture", "architecture:hexagonal"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Cqrs And Event Sourcing", "type": "course", "chapters": 10, "slides": 295, "folder": "courses/architecting/cqrs-and-event-sourcing", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/cqrs-and-event-sourcing.pdf", "level": "advanced", "category": "architecture", "duration_hours": 16, "tags": ["architecture:cqrs", "architecture:event-sourcing", "concepts:distributed-systems", "practices:ddd"], "audience": ["audiences:architects", "audiences:developers"]}, {"name": "Disaster Recovery", "type": "course", "chapters": 6, "slides": 84, "folder": "courses/architecting/disaster-recovery", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/disaster-recovery.pdf", "level": "intermediate", "category": "architecting", "duration_hours": 16, "tags": ["architecting:patterns", "practices:reliability"], "audience": ["audiences:architects", "audiences:devops"]}, {"name": "Distributed Systems Fundamentals", "type": "course", "chapters": 11, "slides": 195, "folder": "courses/architecting/distributed-systems-fundamentals", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/distributed-systems-fundamentals.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 24, "tags": ["architecture:distributed-systems", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Domain Driven Design", "type": "course", "chapters": 8, "slides": 173, "folder": "courses/architecting/domain-driven-design", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/domain-driven-design.pdf", "level": "advanced", "category": "architecture", "duration_hours": 24, "tags": ["concepts:domain-driven-design", "concepts:architecture", "concepts:design-patterns"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Event Driven Architecture", "type": "course", "chapters": 8, "slides": 199, "folder": "courses/architecting/event-driven-architecture", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/event-driven-architecture.pdf", "level": "intermediate", "category": "architecting", "duration_hours": 16, "tags": ["architecting:patterns"], "audience": ["audiences:architects"]}, {"name": "Legacy Modernization", "type": "course", "chapters": 6, "slides": 85, "folder": "courses/architecting/legacy-modernization", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/legacy-modernization.pdf", "level": "intermediate", "category": "architecting", "duration_hours": 16, "tags": ["architecting:patterns"], "audience": ["audiences:architects"]}, {"name": "Message Queues", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/architecting/message-queues", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/message-queues.pdf", "level": "intermediate", "category": "architecting", "duration_hours": 16, "tags": ["architecting:patterns", "queues:overview"], "audience": ["audiences:architects", "audiences:developers"]}, {"name": "Microservices Architecture", "type": "course", "chapters": 15, "slides": 256, "folder": "courses/architecting/microservices-architecture", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/microservices-architecture.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["concepts:microservices", "concepts:architecture", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:architects", "audiences:devops"]}, {"name": "Saga Pattern", "type": "course", "chapters": 7, "slides": 172, "folder": "courses/architecting/saga-pattern", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/saga-pattern.pdf", "level": "advanced", "category": "architecture", "duration_hours": 8, "tags": ["architecture:saga", "architecture:distributed-transactions", "concepts:microservices", "concepts:eventual-consistency"], "audience": ["audiences:architects", "audiences:developers"]}, {"name": "Serverless Architecture", "type": "course", "chapters": 10, "slides": 176, "folder": "courses/architecting/serverless-architecture", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/serverless-architecture.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["architecture:serverless", "infrastructure:cloud"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Site Reliability Engineering", "type": "course", "chapters": 9, "slides": 100, "folder": "courses/architecting/site-reliability-engineering", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/site-reliability-engineering.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 24, "tags": ["practices:sre", "practices:devops", "concepts:architecture"], "audience": ["audiences:developers", "audiences:devops", "audiences:managers"]}, {"name": "System Design", "type": "course", "chapters": 12, "slides": 195, "folder": "courses/architecting/system-design", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/system-design.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 24, "tags": ["architecture:system-design", "concepts:scalability"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Twelve Factor App", "type": "course", "chapters": 16, "slides": 216, "folder": "courses/architecting/twelve-factor-app", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/twelve-factor-app.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 16, "tags": ["concepts:architecture", "concepts:best-practices", "practices:devops", "infrastructure:containers"], "audience": ["audiences:developers", "audiences:architects", "audiences:devops"]}, {"name": "Web Architecture And Scaling", "type": "course", "chapters": 6, "slides": 86, "folder": "courses/architecting/web-architecture-and-scaling", "folder_label": "Architecting", "pdf": "/teaching-slides/pdfunite/architecting/web-architecture-and-scaling.pdf", "level": "intermediate", "category": "architecting", "duration_hours": 16, "tags": ["architecting:patterns", "practices:scalability"], "audience": ["audiences:architects"]}, {"name": "Advanced Spark With Python", "type": "course", "chapters": 11, "slides": 614, "folder": "courses/big_data/advanced-spark-with-python", "folder_label": "Big Data", "pdf": "/teaching-slides/pdfunite/big_data/advanced-spark-with-python.pdf", "level": "advanced", "category": "big-data", "duration_hours": 24, "tags": ["tools:spark", "languages:python", "data-and-ai:big-data", "practices:performance", "data-and-ai:machine-learning"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Apache Spark With Python", "type": "course", "chapters": 8, "slides": 178, "folder": "courses/big_data/apache-spark-with-python", "folder_label": "Big Data", "pdf": "/teaching-slides/pdfunite/big_data/apache-spark-with-python.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 24, "tags": ["tools:spark", "languages:python", "data-and-ai:big-data", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Apache Spark With Scala", "type": "course", "chapters": 10, "slides": 285, "folder": "courses/big_data/apache-spark-with-scala", "folder_label": "Big Data", "pdf": "/teaching-slides/pdfunite/big_data/apache-spark-with-scala.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 24, "tags": ["tools:spark", "languages:scala", "data-and-ai:big-data", "concepts:distributed-systems"], "audience": ["audiences:developers"]}, {"name": "Cmake", "type": "course", "chapters": 9, "slides": 253, "folder": "courses/build_systems/cmake", "folder_label": "Build Systems", "pdf": "/teaching-slides/pdfunite/build_systems/cmake.pdf", "level": "intermediate", "category": "build-system", "duration_hours": 16, "tags": ["tools:cmake", "languages:c", "languages:c++", "practices:build-systems"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Make", "type": "course", "chapters": 6, "slides": 113, "folder": "courses/build_systems/make", "folder_label": "Build Systems", "pdf": "/teaching-slides/pdfunite/build_systems/make.pdf", "level": "intermediate", "category": "build-system", "duration_hours": 16, "tags": ["tools:make", "languages:c", "practices:build-systems", "infrastructure:linux"], "audience": ["audiences:developers"]}, {"name": "Architecting In The Cloud", "type": "course", "chapters": 14, "slides": 449, "folder": "courses/cloud/architecting-in-the-cloud", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/architecting-in-the-cloud.pdf", "level": "intermediate", "category": "cloud", "duration_hours": 32, "tags": ["infrastructure:cloud", "concepts:architecture", "concepts:scalability", "concepts:design-patterns"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:architects", "audiences:devops"]}, {"name": "Finops", "type": "course", "chapters": 12, "slides": 200, "folder": "courses/cloud/finops", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/finops.pdf", "level": "intermediate", "category": "cloud", "duration_hours": 11, "tags": ["infrastructure:cloud", "infrastructure:onprem", "practices:finops", "practices:cost-optimization", "concepts:cloud-economics"], "audience": ["audiences:devops", "audiences:architects", "audiences:managers"]}, {"name": "Introduction To Aws", "type": "course", "chapters": 9, "slides": 246, "folder": "courses/cloud/introduction-to-aws", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/introduction-to-aws.pdf", "level": "beginner", "category": "cloud", "duration_hours": 16, "tags": ["infrastructure:cloud", "infrastructure:aws"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:managers"]}, {"name": "Introduction To Azure", "type": "course", "chapters": 11, "slides": 315, "folder": "courses/cloud/introduction-to-azure", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/introduction-to-azure.pdf", "level": "beginner", "category": "cloud", "duration_hours": 24, "tags": ["infrastructure:cloud", "infrastructure:azure", "practices:devops", "infrastructure:iaas", "infrastructure:paas"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Introduction To Cloud Computing", "type": "course", "chapters": 14, "slides": 233, "folder": "courses/cloud/introduction-to-cloud-computing", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/introduction-to-cloud-computing.pdf", "level": "beginner", "category": "cloud", "duration_hours": 16, "tags": ["infrastructure:cloud"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops", "audiences:managers"]}, {"name": "Multi Cloud Strategy", "type": "course", "chapters": 14, "slides": 257, "folder": "courses/cloud/multi-cloud-strategy", "folder_label": "Cloud", "pdf": "/teaching-slides/pdfunite/cloud/multi-cloud-strategy.pdf", "level": "advanced", "category": "cloud", "duration_hours": 16, "tags": ["infrastructure:cloud", "infrastructure:aws", "infrastructure:azure", "infrastructure:gcp", "concepts:architecture"], "audience": ["audiences:architects", "audiences:managers"]}, {"name": "Docker Fundamentals", "type": "course", "chapters": 9, "slides": 159, "folder": "courses/containers/docker-fundamentals", "folder_label": "Containers", "pdf": "/teaching-slides/pdfunite/containers/docker-fundamentals.pdf", "level": "beginner", "category": "containers", "duration_hours": 16, "tags": ["infrastructure:docker", "infrastructure:containers", "practices:devops"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Kubernetes", "type": "course", "chapters": 11, "slides": 185, "folder": "courses/containers/kubernetes", "folder_label": "Containers", "pdf": "/teaching-slides/pdfunite/containers/kubernetes.pdf", "level": "intermediate", "category": "containers", "duration_hours": 24, "tags": ["infrastructure:kubernetes", "infrastructure:containers"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Data Analytics For Managers", "type": "course", "chapters": 10, "slides": 172, "folder": "courses/data_driven/data-analytics-for-managers", "folder_label": "Data Driven", "pdf": "/teaching-slides/pdfunite/data_driven/data-analytics-for-managers.pdf", "level": "beginner", "category": "data-driven", "duration_hours": 32, "tags": ["data-and-ai:data-analytics", "data-and-ai:business-intelligence"], "audience": ["audiences:managers"]}, {"name": "Apache Airflow", "type": "course", "chapters": 10, "slides": 157, "folder": "courses/data_engineering/apache-airflow", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/apache-airflow.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:airflow", "data-and-ai:orchestration"], "audience": ["audiences:data-engineers", "audiences:developers"]}, {"name": "Data Lakehouse", "type": "course", "chapters": 6, "slides": 86, "folder": "courses/data_engineering/data-lakehouse", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/data-lakehouse.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:data-engineering"], "audience": ["audiences:data-engineers", "audiences:architects"]}, {"name": "Databricks", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/data_engineering/databricks", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/databricks.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:data-engineering"], "audience": ["audiences:data-engineers"]}, {"name": "Dbt", "type": "course", "chapters": 10, "slides": 163, "folder": "courses/data_engineering/dbt", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/dbt.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:dbt", "data-and-ai:transformation"], "audience": ["audiences:data-engineers", "audiences:developers"]}, {"name": "Etl", "type": "course", "chapters": 6, "slides": 86, "folder": "courses/data_engineering/etl", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/etl.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:data-engineering"], "audience": ["audiences:data-engineers"]}, {"name": "Snowflake", "type": "course", "chapters": 6, "slides": 86, "folder": "courses/data_engineering/snowflake", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/snowflake.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 16, "tags": ["data-and-ai:data-engineering"], "audience": ["audiences:data-engineers"]}, {"name": "Spark", "type": "course", "chapters": 6, "slides": 88, "folder": "courses/data_engineering/spark", "folder_label": "Data Engineering", "pdf": "/teaching-slides/pdfunite/data_engineering/spark.pdf", "level": "intermediate", "category": "data-engineering", "duration_hours": 24, "tags": ["data-and-ai:big-data"], "audience": ["audiences:data-engineers"]}, {"name": "Data Analyst Fundamentals", "type": "course", "chapters": 13, "slides": 242, "folder": "courses/data_science/data-analyst-fundamentals", "folder_label": "Data Science", "pdf": "/teaching-slides/pdfunite/data_science/data-analyst-fundamentals.pdf", "level": "beginner", "category": "data-science", "duration_hours": 24, "tags": ["data-and-ai:data-analysis", "data-and-ai:statistics", "languages:python", "languages:sql"], "audience": ["audiences:data-analysts", "audiences:developers"]}, {"name": "Cassandra", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/databases/cassandra", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/cassandra.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:cassandra"], "audience": ["audiences:developers", "audiences:dba"]}, {"name": "Clickhouse", "type": "course", "chapters": 6, "slides": 86, "folder": "courses/databases/clickhouse", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/clickhouse.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:clickhouse"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Cockroachdb", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/databases/cockroachdb", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/cockroachdb.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:cockroachdb"], "audience": ["audiences:developers", "audiences:dba"]}, {"name": "Database Design", "type": "course", "chapters": 9, "slides": 120, "folder": "courses/databases/database-design", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/database-design.pdf", "level": "intermediate", "category": "databases", "duration_hours": 8, "tags": ["databases:design", "databases:relational"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Database Migration Strategies", "type": "course", "chapters": 6, "slides": 88, "folder": "courses/databases/database-migration-strategies", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/database-migration-strategies.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:migrations", "practices:migration"], "audience": ["audiences:dba", "audiences:architects"]}, {"name": "Duckdb", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/databases/duckdb", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/duckdb.pdf", "level": "intermediate", "category": "databases", "duration_hours": 8, "tags": ["databases:duckdb"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Dynamodb", "type": "course", "chapters": 6, "slides": 89, "folder": "courses/databases/dynamodb", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/dynamodb.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:dynamodb"], "audience": ["audiences:developers"]}, {"name": "Elasticsearch Administration", "type": "course", "chapters": 21, "slides": 382, "folder": "courses/databases/elasticsearch-administration", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/elasticsearch-administration.pdf", "level": "intermediate", "category": "databases", "duration_hours": 40, "tags": ["databases:elasticsearch", "data-and-ai:search", "concepts:distributed-systems"], "audience": ["audiences:dbas", "audiences:sysadmins", "audiences:architects", "audiences:devops"]}, {"name": "Elasticsearch For Developers", "type": "course", "chapters": 18, "slides": 296, "folder": "courses/databases/elasticsearch-for-developers", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/elasticsearch-for-developers.pdf", "level": "intermediate", "category": "databases", "duration_hours": 40, "tags": ["databases:elasticsearch", "data-and-ai:search"], "audience": ["audiences:developers"]}, {"name": "Introduction To Databases", "type": "course", "chapters": 11, "slides": 173, "folder": "courses/databases/introduction-to-databases", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/introduction-to-databases.pdf", "level": "beginner", "category": "databases", "duration_hours": 24, "tags": ["databases:relational", "databases:nosql"], "audience": ["audiences:developers"]}, {"name": "Mongodb For Developers", "type": "course", "chapters": 16, "slides": 265, "folder": "courses/databases/mongodb-for-developers", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/mongodb-for-developers.pdf", "level": "intermediate", "category": "databases", "duration_hours": 24, "tags": ["databases:mongodb", "databases:nosql"], "audience": ["audiences:developers"]}, {"name": "Neo4J", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/databases/neo4j", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/neo4j.pdf", "level": "intermediate", "category": "databases", "duration_hours": 16, "tags": ["databases:neo4j"], "audience": ["audiences:developers"]}, {"name": "Postgresql For Developers", "type": "course", "chapters": 10, "slides": 150, "folder": "courses/databases/postgresql-for-developers", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/postgresql-for-developers.pdf", "level": "intermediate", "category": "databases", "duration_hours": 24, "tags": ["databases:postgresql", "databases:sql"], "audience": ["audiences:developers"]}, {"name": "Redis", "type": "course", "chapters": 10, "slides": 400, "folder": "courses/databases/redis", "folder_label": "Databases", "pdf": "/teaching-slides/pdfunite/databases/redis.pdf", "level": "intermediate", "category": "database", "duration_hours": 24, "tags": ["tools:redis", "data-and-ai:nosql", "data-and-ai:caching", "concepts:data-structures"], "audience": ["audiences:developers"]}, {"name": "Design Patterns", "type": "course", "chapters": 5, "slides": 86, "folder": "courses/design_patterns/design-patterns", "folder_label": "Design Patterns", "pdf": "/teaching-slides/pdfunite/design_patterns/design-patterns.pdf", "level": "intermediate", "category": "design-patterns", "duration_hours": 24, "tags": ["concepts:design-patterns", "concepts:oop"], "audience": ["audiences:developers"]}, {"name": "Code Review Best Practices", "type": "course", "chapters": 16, "slides": 288, "folder": "courses/development_methodologies/code-review-best-practices", "folder_label": "Development Methodologies", "pdf": "/teaching-slides/pdfunite/development_methodologies/code-review-best-practices.pdf", "level": "beginner", "category": "methodology", "duration_hours": 16, "tags": ["practices:methodology", "concepts:code-review"], "audience": ["audiences:developers", "audiences:managers"]}, {"name": "Technical Writing", "type": "course", "chapters": 15, "slides": 283, "folder": "courses/development_methodologies/technical-writing", "folder_label": "Development Methodologies", "pdf": "/teaching-slides/pdfunite/development_methodologies/technical-writing.pdf", "level": "beginner", "category": "methodology", "duration_hours": 16, "tags": ["practices:methodology", "concepts:best-practices"], "audience": ["audiences:developers", "audiences:managers"]}, {"name": "Advanced Docker", "type": "course", "chapters": 7, "slides": 217, "folder": "courses/devops/advanced-docker", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/advanced-docker.pdf", "level": "advanced", "category": "devops", "duration_hours": 16, "tags": ["tools:docker", "infrastructure:containers", "practices:devops", "networking:networking"], "audience": ["audiences:developers"]}, {"name": "Advanced Kubernetes", "type": "course", "chapters": 16, "slides": 356, "folder": "courses/devops/advanced-kubernetes", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/advanced-kubernetes.pdf", "level": "advanced", "category": "devops", "duration_hours": 24, "tags": ["tools:kubernetes", "infrastructure:containers", "practices:devops", "languages:go", "concepts:service-mesh"], "audience": ["audiences:developers"]}, {"name": "Ansible", "type": "course", "chapters": 18, "slides": 496, "folder": "courses/devops/ansible", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/ansible.pdf", "level": "intermediate", "category": "devops", "duration_hours": 16, "tags": ["practices:devops", "tools:ansible", "infrastructure:configuration-management", "infrastructure:cloud", "practices:automation"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Architectural Decisions In Devops", "type": "course", "chapters": 16, "slides": 720, "folder": "courses/devops/architectural-decisions-in-devops", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/architectural-decisions-in-devops.pdf", "level": "advanced", "category": "devops", "duration_hours": 24, "tags": ["practices:devops", "concepts:architecture", "practices:ci-cd", "infrastructure:infrastructure-as-code"], "audience": ["audiences:architects", "audiences:devops", "audiences:managers"]}, {"name": "Docker For Developers", "type": "course", "chapters": 14, "slides": 192, "folder": "courses/devops/docker-for-developers", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/docker-for-developers.pdf", "level": "intermediate", "category": "devops", "duration_hours": 24, "tags": ["tools:docker", "infrastructure:containers", "practices:devops", "networking:networking"], "audience": ["audiences:developers"]}, {"name": "Github Workflows", "type": "course", "chapters": 9, "slides": 124, "folder": "courses/devops/github-workflows", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/github-workflows.pdf", "level": "intermediate", "category": "devops", "duration_hours": 8, "tags": ["tools:github", "practices:ci-cd", "practices:automation", "practices:devops"], "audience": ["audiences:developers", "audiences:devops", "audiences:managers"]}, {"name": "K8S Introduction", "type": "course", "chapters": 16, "slides": 599, "folder": "courses/devops/k8s-introduction", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/k8s-introduction.pdf", "level": "beginner", "category": "devops", "duration_hours": 40, "tags": ["tools:kubernetes", "infrastructure:containers", "infrastructure:orchestration", "practices:devops", "tools:docker"], "audience": ["audiences:developers", "audiences:devops", "audiences:sysadmins"]}, {"name": "Terraform", "type": "course", "chapters": 16, "slides": 467, "folder": "courses/devops/terraform", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/terraform.pdf", "level": "intermediate", "category": "devops", "duration_hours": 24, "tags": ["practices:devops", "tools:terraform", "infrastructure:infrastructure-as-code", "infrastructure:cloud", "tools:terragrunt"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Welcome To The World Of Devops", "type": "course", "chapters": 14, "slides": 221, "folder": "courses/devops/welcome-to-the-world-of-devops", "folder_label": "Devops", "pdf": "/teaching-slides/pdfunite/devops/welcome-to-the-world-of-devops.pdf", "level": "beginner", "category": "devops", "duration_hours": 40, "tags": ["practices:devops", "practices:ci-cd", "practices:automation"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops", "audiences:managers"]}, {"name": "Effective Real Time Embedded C And C++", "type": "course", "chapters": 20, "slides": 643, "folder": "courses/embedded/effective-real-time-embedded-c-and-c++", "folder_label": "Embedded", "pdf": "/teaching-slides/pdfunite/embedded/effective-real-time-embedded-c-and-c++.pdf", "level": "advanced", "category": "embedded", "duration_hours": 32, "tags": ["hardware-and-embedded:embedded", "infrastructure:real-time", "languages:c", "languages:c++"], "audience": ["audiences:embedded-engineers", "audiences:developers"]}, {"name": "Stm32 Nucleo Wl55Jc1 Firmware", "type": "course", "chapters": 11, "slides": 142, "folder": "courses/embedded/stm32-nucleo-wl55jc1-firmware", "folder_label": "Embedded", "pdf": "/teaching-slides/pdfunite/embedded/stm32-nucleo-wl55jc1-firmware.pdf", "level": "advanced", "category": "embedded", "duration_hours": 24, "tags": ["hardware-and-embedded:embedded", "hardware-and-embedded:hardware-programming"], "audience": ["audiences:embedded-engineers", "audiences:developers"]}, {"name": "Advanced Git", "type": "course", "chapters": 10, "slides": 226, "folder": "courses/git/advanced-git", "folder_label": "Git", "pdf": "/teaching-slides/pdfunite/git/advanced-git.pdf", "level": "advanced", "category": "version-control", "duration_hours": 16, "tags": ["tools:git", "concepts:version-control", "practices:devops"], "audience": ["audiences:developers", "audiences:devops", "audiences:team-leads"]}, {"name": "Git", "type": "course", "chapters": 22, "slides": 750, "folder": "courses/git/git", "folder_label": "Git", "pdf": "/teaching-slides/pdfunite/git/git.pdf", "level": "intermediate", "category": "version-control", "duration_hours": 56, "tags": ["tools:git", "concepts:version-control"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops", "audiences:managers"]}, {"name": "Computer Architecture Fundamentals", "type": "course", "chapters": 7, "slides": 300, "folder": "courses/hardware/computer-architecture-fundamentals", "folder_label": "Hardware", "pdf": "/teaching-slides/pdfunite/hardware/computer-architecture-fundamentals.pdf", "level": "beginner", "category": "hardware", "duration_hours": 8, "tags": ["concepts:computer-architecture", "concepts:hardware", "concepts:performance", "concepts:security"], "audience": ["audiences:developers", "audiences:sysadmins"]}, {"name": "Assembly Programming Using Gas", "type": "course", "chapters": 21, "slides": 271, "folder": "courses/languages/assembly/assembly-programming-using-gas", "folder_label": "Languages / Assembly", "pdf": "/teaching-slides/pdfunite/languages/assembly/assembly-programming-using-gas.pdf", "level": "advanced", "category": "language", "duration_hours": 32, "tags": ["languages:assembly", "hardware-and-embedded:x86", "infrastructure:linux", "infrastructure:low-level", "practices:performance"], "audience": ["audiences:developers"]}, {"name": "Bash Scripting", "type": "course", "chapters": 26, "slides": 366, "folder": "courses/languages/bash/bash-scripting", "folder_label": "Languages / Bash", "pdf": "/teaching-slides/pdfunite/languages/bash/bash-scripting.pdf", "level": "intermediate", "category": "language", "duration_hours": 24, "tags": ["languages:bash", "practices:scripting", "infrastructure:linux", "practices:automation"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "C Refresher", "type": "course", "chapters": 16, "slides": 351, "folder": "courses/languages/c/c-refresher", "folder_label": "Languages / C", "pdf": "/teaching-slides/pdfunite/languages/c/c-refresher.pdf", "level": "intermediate", "category": "language", "duration_hours": 24, "tags": ["languages:c", "concepts:programming", "concepts:memory-management", "concepts:pointers"], "audience": ["audiences:developers"]}, {"name": "C++ Design Patterns", "type": "course", "chapters": 26, "slides": 248, "folder": "courses/languages/c++/c++-design-patterns", "folder_label": "Languages / C++", "pdf": "/teaching-slides/pdfunite/languages/c++/c++-design-patterns.pdf", "level": "advanced", "category": "language", "duration_hours": 8, "tags": ["languages:cpp", "concepts:design-patterns", "concepts:oop", "practices:software-design"], "audience": ["audiences:developers"]}, {"name": "Modern C++ For C Programmers", "type": "course", "chapters": 19, "slides": 791, "folder": "courses/languages/c++/modern-c++-for-c-programmers", "folder_label": "Languages / C++", "pdf": "/teaching-slides/pdfunite/languages/c++/modern-c++-for-c-programmers.pdf", "level": "intermediate", "category": "language", "duration_hours": 40, "tags": ["languages:c++", "languages:c", "languages:c++11", "languages:c++17", "concepts:oop", "concepts:design-patterns"], "audience": ["audiences:developers"]}, {"name": "Advanced Python", "type": "course", "chapters": 21, "slides": 955, "folder": "courses/languages/python/advanced-python", "folder_label": "Languages / Python", "pdf": "/teaching-slides/pdfunite/languages/python/advanced-python.pdf", "level": "advanced", "category": "language", "duration_hours": 56, "tags": ["languages:python", "practices:performance", "concepts:concurrency", "concepts:data-structures"], "audience": ["audiences:developers"]}, {"name": "Python Programming", "type": "course", "chapters": 15, "slides": 523, "folder": "courses/languages/python/python-programming", "folder_label": "Languages / Python", "pdf": "/teaching-slides/pdfunite/languages/python/python-programming.pdf", "level": "beginner", "category": "language", "duration_hours": 40, "tags": ["languages:python", "concepts:programming", "practices:scripting", "practices:automation", "concepts:oop"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:data-scientists", "audiences:devops"]}, {"name": "Advanced Rust", "type": "course", "chapters": 10, "slides": 457, "folder": "courses/languages/rust/advanced-rust", "folder_label": "Languages / Rust", "pdf": "/teaching-slides/pdfunite/languages/rust/advanced-rust.pdf", "level": "advanced", "category": "language", "duration_hours": 24, "tags": ["languages:rust", "concepts:programming"], "audience": ["audiences:developers"]}, {"name": "Rust Programming", "type": "course", "chapters": 12, "slides": 319, "folder": "courses/languages/rust/rust-programming", "folder_label": "Languages / Rust", "pdf": "/teaching-slides/pdfunite/languages/rust/rust-programming.pdf", "level": "beginner", "category": "language", "duration_hours": 32, "tags": ["languages:rust", "concepts:programming", "concepts:concurrency", "concepts:systems-programming"], "audience": ["audiences:developers"]}, {"name": "Deep Learning Fundamentals", "type": "course", "chapters": 8, "slides": 327, "folder": "courses/machine_learning/deep-learning-fundamentals", "folder_label": "Machine Learning", "pdf": "/teaching-slides/pdfunite/machine_learning/deep-learning-fundamentals.pdf", "level": "intermediate", "category": "machine-learning", "duration_hours": 24, "tags": ["data-and-ai:deep-learning", "data-and-ai:ml", "languages:python", "tools:pytorch", "tools:tensorflow"], "audience": ["audiences:developers", "audiences:data-scientists", "audiences:architects"]}, {"name": "Machine Learning", "type": "course", "chapters": 14, "slides": 704, "folder": "courses/machine_learning/machine-learning", "folder_label": "Machine Learning", "pdf": "/teaching-slides/pdfunite/machine_learning/machine-learning.pdf", "level": "intermediate", "category": "machine-learning", "duration_hours": 40, "tags": ["data-and-ai:machine-learning"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Statistics Applied", "type": "course", "chapters": 16, "slides": 191, "folder": "courses/math/statistics-applied", "folder_label": "Math", "pdf": "/teaching-slides/pdfunite/math/statistics-applied.pdf", "level": "beginner", "category": "math", "duration_hours": 24, "tags": ["math:statistics", "math:probability", "math:descriptive-statistics", "languages:python"], "audience": ["audiences:data-analysts", "audiences:developers", "audiences:analysts"]}, {"name": "Statistics Inference", "type": "course", "chapters": 16, "slides": 193, "folder": "courses/math/statistics-inference", "folder_label": "Math", "pdf": "/teaching-slides/pdfunite/math/statistics-inference.pdf", "level": "intermediate", "category": "math", "duration_hours": 32, "tags": ["math:inferential-statistics", "math:hypothesis-testing", "math:regression", "languages:python"], "audience": ["audiences:data-analysts", "audiences:data-scientists", "audiences:developers"]}, {"name": "Statistics Theory", "type": "course", "chapters": 16, "slides": 177, "folder": "courses/math/statistics-theory", "folder_label": "Math", "pdf": "/teaching-slides/pdfunite/math/statistics-theory.pdf", "level": "advanced", "category": "math", "duration_hours": 40, "tags": ["math:probability", "math:inferential-statistics", "math:estimation", "languages:python"], "audience": ["audiences:data-scientists", "audiences:ml-engineers", "audiences:senior-developers"]}, {"name": "Dns Deep Dive", "type": "course", "chapters": 8, "slides": 208, "folder": "courses/networking/dns-deep-dive", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/dns-deep-dive.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["networking:dns", "protocols:dns", "infrastructure:networking", "concepts:internet-infrastructure"], "audience": ["audiences:sysadmins", "audiences:devops", "audiences:network-engineers", "audiences:developers"]}, {"name": "Graphql", "type": "course", "chapters": 13, "slides": 205, "folder": "courses/networking/graphql", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/graphql.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["networking:graphql", "networking:api"], "audience": ["audiences:developers"]}, {"name": "Grpc", "type": "course", "chapters": 8, "slides": 192, "folder": "courses/networking/grpc", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/grpc.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["networking:grpc"], "audience": ["audiences:developers"]}, {"name": "Linux Networking Overview", "type": "course", "chapters": 11, "slides": 266, "folder": "courses/networking/linux-networking-overview", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/linux-networking-overview.pdf", "level": "intermediate", "category": "networking", "duration_hours": 24, "tags": ["networking:networking", "networking:tcp-ip", "infrastructure:linux", "concepts:protocols"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Network Security", "type": "course", "chapters": 6, "slides": 87, "folder": "courses/networking/network-security", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/network-security.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["security:network"], "audience": ["audiences:devops", "audiences:security"]}, {"name": "Networking Basics", "type": "course", "chapters": 9, "slides": 321, "folder": "courses/networking/networking-basics", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/networking-basics.pdf", "level": "beginner", "category": "networking", "duration_hours": 16, "tags": ["networking:networking", "networking:tcp-ip", "networking:http", "networking:protocols"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Oauth2 And Oidc", "type": "course", "chapters": 10, "slides": 259, "folder": "courses/networking/oauth2-and-oidc", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/oauth2-and-oidc.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["security:authentication", "security:authorization"], "audience": ["audiences:developers", "audiences:security"]}, {"name": "Restful Apis", "type": "course", "chapters": 10, "slides": 153, "folder": "courses/networking/restful-apis", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/restful-apis.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["networking:rest", "networking:http"], "audience": ["audiences:developers"]}, {"name": "Tcp Ip Deep Dive", "type": "course", "chapters": 9, "slides": 224, "folder": "courses/networking/tcp-ip-deep-dive", "folder_label": "Networking", "pdf": "/teaching-slides/pdfunite/networking/tcp-ip-deep-dive.pdf", "level": "intermediate", "category": "networking", "duration_hours": 16, "tags": ["networking:tcp-ip", "networking:protocols", "infrastructure:networking"], "audience": ["audiences:developers", "audiences:devops", "audiences:network-engineers"]}, {"name": "Grafana Basics", "type": "course", "chapters": 6, "slides": 89, "folder": "courses/observability_and_monitoring/grafana-basics", "folder_label": "Observability And Monitoring", "pdf": "/teaching-slides/pdfunite/observability_and_monitoring/grafana-basics.pdf", "level": "beginner", "category": "observability", "duration_hours": 8, "tags": ["observability:grafana"], "audience": ["audiences:devops"]}, {"name": "Jaeger", "type": "course", "chapters": 6, "slides": 90, "folder": "courses/observability_and_monitoring/jaeger", "folder_label": "Observability And Monitoring", "pdf": "/teaching-slides/pdfunite/observability_and_monitoring/jaeger.pdf", "level": "intermediate", "category": "observability", "duration_hours": 8, "tags": ["observability:tracing"], "audience": ["audiences:devops", "audiences:developers"]}, {"name": "Opentelemetry", "type": "course", "chapters": 11, "slides": 181, "folder": "courses/observability_and_monitoring/opentelemetry", "folder_label": "Observability And Monitoring", "pdf": "/teaching-slides/pdfunite/observability_and_monitoring/opentelemetry.pdf", "level": "intermediate", "category": "observability-and-monitoring", "duration_hours": 16, "tags": ["infrastructure:opentelemetry", "practices:observability"], "audience": ["audiences:developers"]}, {"name": "Prometheus And Grafana", "type": "course", "chapters": 7, "slides": 107, "folder": "courses/observability_and_monitoring/prometheus-and-grafana", "folder_label": "Observability And Monitoring", "pdf": "/teaching-slides/pdfunite/observability_and_monitoring/prometheus-and-grafana.pdf", "level": "intermediate", "category": "observability-and-monitoring", "duration_hours": 16, "tags": ["infrastructure:prometheus", "infrastructure:grafana"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Advanced Android Application Development", "type": "course", "chapters": 16, "slides": 229, "folder": "courses/operating_systems/advanced-android-application-development", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/advanced-android-application-development.pdf", "level": "advanced", "category": "mobile", "duration_hours": 40, "tags": ["infrastructure:android", "languages:java", "concepts:mobile-development", "concepts:oop", "practices:software-design"], "audience": ["audiences:developers"]}, {"name": "Embedded Linux Platform Development With Yocto", "type": "course", "chapters": 12, "slides": 406, "folder": "courses/operating_systems/embedded-linux-platform-development-with-yocto", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/embedded-linux-platform-development-with-yocto.pdf", "level": "advanced", "category": "embedded", "duration_hours": 32, "tags": ["infrastructure:linux", "infrastructure:embedded", "tools:yocto", "concepts:cross-compilation", "practices:build-systems"], "audience": ["audiences:developers", "audiences:sysadmins"]}, {"name": "Linux Fundamentals", "type": "course", "chapters": 13, "slides": 259, "folder": "courses/operating_systems/linux-fundamentals", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/linux-fundamentals.pdf", "level": "beginner", "category": "operating-systems", "duration_hours": 24, "tags": ["infrastructure:linux", "infrastructure:unix", "languages:shell", "practices:command-line", "audiences:sysadmin"], "audience": ["audiences:developers", "audiences:sysadmins"]}, {"name": "Linux Kernel Advanced Topics", "type": "course", "chapters": 12, "slides": 436, "folder": "courses/operating_systems/linux-kernel-advanced-topics", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/linux-kernel-advanced-topics.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 32, "tags": ["infrastructure:linux", "concepts:kernel", "concepts:device-drivers", "concepts:bsp", "infrastructure:embedded"], "audience": ["audiences:developers", "audiences:sysadmins"]}, {"name": "Linux Package Managers", "type": "course", "chapters": 8, "slides": 128, "folder": "courses/operating_systems/linux-package-managers", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/linux-package-managers.pdf", "level": "intermediate", "category": "operating-systems", "duration_hours": 16, "tags": ["infrastructure:linux", "infrastructure:unix", "practices:command-line", "audiences:sysadmin", "audiences:devops"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Linux System Administration", "type": "course", "chapters": 15, "slides": 561, "folder": "courses/operating_systems/linux-system-administration", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/linux-system-administration.pdf", "level": "intermediate", "category": "operating-systems", "duration_hours": 40, "tags": ["infrastructure:linux", "audiences:sysadmin", "infrastructure:storage", "networking:networking", "security:security", "practices:monitoring"], "audience": ["audiences:sysadmins", "audiences:devops"]}, {"name": "Linux Systems Programming", "type": "course", "chapters": 24, "slides": 851, "folder": "courses/operating_systems/linux-systems-programming", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/linux-systems-programming.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 64, "tags": ["infrastructure:linux", "languages:c", "concepts:systems-programming", "concepts:multithreading", "infrastructure:ipc", "networking:networking", "infrastructure:io"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Qemu For Kernel Developers", "type": "course", "chapters": 10, "slides": 313, "folder": "courses/operating_systems/qemu-for-kernel-developers", "folder_label": "Operating Systems", "pdf": "/teaching-slides/pdfunite/operating_systems/qemu-for-kernel-developers.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 24, "tags": ["tools:qemu", "infrastructure:virtualization", "concepts:kernel", "infrastructure:linux", "practices:debugging"], "audience": ["audiences:developers"]}, {"name": "Agile And Scrum", "type": "course", "chapters": 9, "slides": 140, "folder": "courses/practices/agile-and-scrum", "folder_label": "Practices", "pdf": "/teaching-slides/pdfunite/practices/agile-and-scrum.pdf", "level": "beginner", "category": "practices", "duration_hours": 8, "tags": ["practices:agile", "practices:scrum", "practices:project-management"], "audience": ["audiences:developers", "audiences:team-leads"]}, {"name": "Object Oriented Programming", "type": "course", "chapters": 12, "slides": 199, "folder": "courses/principles/object-oriented-programming", "folder_label": "Principles", "pdf": "/teaching-slides/pdfunite/principles/object-oriented-programming.pdf", "level": "beginner", "category": "design-patterns", "duration_hours": 16, "tags": ["concepts:oop", "concepts:design-patterns", "concepts:solid", "concepts:programming"], "audience": ["audiences:developers", "audiences:testers"]}, {"name": "Solid Clean Code", "type": "course", "chapters": 9, "slides": 152, "folder": "courses/principles/solid-clean-code", "folder_label": "Principles", "pdf": "/teaching-slides/pdfunite/principles/solid-clean-code.pdf", "level": "intermediate", "category": "design-patterns", "duration_hours": 8, "tags": ["concepts:solid", "concepts:clean-code", "concepts:best-practices"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Kafka", "type": "course", "chapters": 6, "slides": 107, "folder": "courses/queues/kafka", "folder_label": "Queues", "pdf": "/teaching-slides/pdfunite/queues/kafka.pdf", "level": "beginner", "category": "message-queue", "duration_hours": 16, "tags": ["tools:kafka", "data-and-ai:streaming", "concepts:distributed-systems"], "audience": ["audiences:developers"]}, {"name": "Rabbitmq", "type": "course", "chapters": 10, "slides": 192, "folder": "courses/queues/rabbitmq", "folder_label": "Queues", "pdf": "/teaching-slides/pdfunite/queues/rabbitmq.pdf", "level": "intermediate", "category": "message-queue", "duration_hours": 16, "tags": ["tools:rabbitmq", "data-and-ai:message-queues", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:architects"]}, {"name": "Real Time Programming", "type": "course", "chapters": 11, "slides": 202, "folder": "courses/real_time/real-time-programming", "folder_label": "Real Time", "pdf": "/teaching-slides/pdfunite/real_time/real-time-programming.pdf", "level": "advanced", "category": "real-time", "duration_hours": 56, "tags": ["infrastructure:real-time", "languages:c", "infrastructure:linux"], "audience": ["audiences:embedded-engineers", "audiences:developers"]}, {"name": "Cryptography Fundamentals", "type": "course", "chapters": 9, "slides": 104, "folder": "courses/security/cryptography-fundamentals", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/cryptography-fundamentals.pdf", "level": "intermediate", "category": "security", "duration_hours": 24, "tags": ["security:cryptography", "security:tls", "concepts:algorithms"], "audience": ["audiences:developers", "audiences:security-professionals", "audiences:devops"]}, {"name": "Cyber Attacks And Vectors", "type": "course", "chapters": 29, "slides": 611, "folder": "courses/security/cyber-attacks-and-vectors", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/cyber-attacks-and-vectors.pdf", "level": "intermediate", "category": "security", "duration_hours": 40, "tags": ["security:security", "security:cyber-attacks", "security:penetration-testing", "security:vulnerabilities"], "audience": ["audiences:security-professionals", "audiences:developers", "audiences:sysadmins"]}, {"name": "It Security Policies", "type": "course", "chapters": 8, "slides": 136, "folder": "courses/security/it-security-policies", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/it-security-policies.pdf", "level": "beginner", "category": "security", "duration_hours": 8, "tags": ["security:security", "security:policies", "security:compliance"], "audience": ["audiences:managers", "audiences:developers", "audiences:sysadmins", "audiences:security-professionals", "audiences:testers"]}, {"name": "Kubernetes Security", "type": "course", "chapters": 7, "slides": 184, "folder": "courses/security/kubernetes-security", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/kubernetes-security.pdf", "level": "intermediate", "category": "security", "duration_hours": 16, "tags": ["security:kubernetes", "security:cloud-native", "infrastructure:k8s"], "audience": ["audiences:devops", "audiences:security-professionals", "audiences:developers"]}, {"name": "Linux Forensics", "type": "course", "chapters": 14, "slides": 550, "folder": "courses/security/linux-forensics", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/linux-forensics.pdf", "level": "advanced", "category": "security", "duration_hours": 40, "tags": ["infrastructure:linux", "security:forensics", "security:security"], "audience": ["audiences:security-professionals"]}, {"name": "Secure Coding", "type": "course", "chapters": 9, "slides": 103, "folder": "courses/security/secure-coding", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/secure-coding.pdf", "level": "intermediate", "category": "security", "duration_hours": 8, "tags": ["security:secure-coding", "security:owasp", "security:encryption", "security:compliance", "security:application-security", "languages:c", "languages:c++", "languages:python", "practices:ci-cd", "practices:devops", "data-and-ai:ai", "hardware-and-embedded:embedded"], "audience": ["audiences:developers", "audiences:embedded-engineers", "audiences:devops", "audiences:security-professionals"]}, {"name": "Threat Modeling", "type": "course", "chapters": 9, "slides": 219, "folder": "courses/security/threat-modeling", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/threat-modeling.pdf", "level": "intermediate", "category": "security", "duration_hours": 16, "tags": ["security:security", "concepts:architecture", "concepts:best-practices"], "audience": ["audiences:developers", "audiences:security-professionals", "audiences:architects", "audiences:managers"]}, {"name": "Web Application Hacking", "type": "course", "chapters": 22, "slides": 504, "folder": "courses/security/web-application-hacking", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/web-application-hacking.pdf", "level": "advanced", "category": "security", "duration_hours": 40, "tags": ["security:security", "security:web-security", "security:penetration-testing", "security:owasp"], "audience": ["audiences:security-professionals", "audiences:developers", "audiences:testers"]}, {"name": "Working With Llms Securely", "type": "course", "chapters": 12, "slides": 164, "folder": "courses/security/working-with-llms-securely", "folder_label": "Security", "pdf": "/teaching-slides/pdfunite/security/working-with-llms-securely.pdf", "level": "intermediate", "category": "security", "duration_hours": 16, "tags": ["security:security", "data-and-ai:ai", "data-and-ai:llm", "security:owasp"], "audience": ["audiences:developers", "audiences:security-professionals", "audiences:devops"]}, {"name": "Api Testing", "type": "course", "chapters": 8, "slides": 128, "folder": "courses/testing/api-testing", "folder_label": "Testing", "pdf": "/teaching-slides/pdfunite/testing/api-testing.pdf", "level": "intermediate", "category": "testing", "duration_hours": 8, "tags": ["practices:testing", "practices:api"], "audience": ["audiences:developers", "audiences:testers"]}, {"name": "Chaos Engineering", "type": "course", "chapters": 6, "slides": 89, "folder": "courses/testing/chaos-engineering", "folder_label": "Testing", "pdf": "/teaching-slides/pdfunite/testing/chaos-engineering.pdf", "level": "advanced", "category": "testing", "duration_hours": 16, "tags": ["testing:chaos", "practices:reliability"], "audience": ["audiences:devops", "audiences:developers"]}, {"name": "Contract Testing", "type": "course", "chapters": 6, "slides": 90, "folder": "courses/testing/contract-testing", "folder_label": "Testing", "pdf": "/teaching-slides/pdfunite/testing/contract-testing.pdf", "level": "intermediate", "category": "testing", "duration_hours": 8, "tags": ["testing:contract"], "audience": ["audiences:developers", "audiences:testers"]}, {"name": "Performance Testing", "type": "course", "chapters": 6, "slides": 94, "folder": "courses/testing/performance-testing", "folder_label": "Testing", "pdf": "/teaching-slides/pdfunite/testing/performance-testing.pdf", "level": "intermediate", "category": "testing", "duration_hours": 16, "tags": ["testing:performance"], "audience": ["audiences:developers", "audiences:testers"]}, {"name": "Test Driven Development", "type": "course", "chapters": 11, "slides": 214, "folder": "courses/testing/test-driven-development", "folder_label": "Testing", "pdf": "/teaching-slides/pdfunite/testing/test-driven-development.pdf", "level": "intermediate", "category": "testing", "duration_hours": 16, "tags": ["practices:testing", "practices:tdd", "practices:refactoring"], "audience": ["audiences:developers", "audiences:testers"]}, {"name": "Introduction To Game Development With Unity", "type": "course", "chapters": 8, "slides": 132, "folder": "courses/unity/introduction-to-game-development-with-unity", "folder_label": "Unity", "pdf": "/teaching-slides/pdfunite/unity/introduction-to-game-development-with-unity.pdf", "level": "beginner", "category": "game-development", "duration_hours": 24, "tags": ["tools:unity", "practices:game-development", "practices:scripting"], "audience": ["audiences:developers"]}, {"name": "Wifi Protocols", "type": "course", "chapters": 7, "slides": 117, "folder": "courses/wifi/wifi-protocols", "folder_label": "Wifi", "pdf": "/teaching-slides/pdfunite/wifi/wifi-protocols.pdf", "level": "intermediate", "category": "networking", "duration_hours": 24, "tags": ["networking:wifi", "networking:protocols", "networking:802.11"], "audience": ["audiences:developers", "audiences:embedded-engineers"]}, {"name": "Ai Everywhere", "type": "lecture", "chapters": 1, "slides": 30, "folder": "lectures/ai/ai_everywhere", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/ai_everywhere.pdf", "level": "beginner", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:llm", "concepts:agents"], "audience": ["audiences:managers", "audiences:developers"]}, {"name": "Claude Code", "type": "lecture", "chapters": 1, "slides": 40, "folder": "lectures/ai/claude_code", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/claude_code.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:tools"], "audience": ["audiences:developers"]}, {"name": "Context Window", "type": "lecture", "chapters": 1, "slides": 50, "folder": "lectures/ai/context_window", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/context_window.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:prompting"], "audience": ["audiences:developers"]}, {"name": "Ecosystem", "type": "lecture", "chapters": 1, "slides": 52, "folder": "lectures/ai/ecosystem", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/ecosystem.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:llm", "concepts:tools", "concepts:agents"], "audience": ["audiences:developers"]}, {"name": "Llms Large Projects", "type": "lecture", "chapters": 1, "slides": 43, "folder": "lectures/ai/llms_large_projects", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/llms_large_projects.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:architecture", "concepts:microservices"], "audience": ["audiences:developers", "audiences:architects", "audiences:team-leads"]}, {"name": "Mcp", "type": "lecture", "chapters": 1, "slides": 45, "folder": "lectures/ai/mcp", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/mcp.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:tools", "concepts:mcp"], "audience": ["audiences:developers"]}, {"name": "Roles", "type": "lecture", "chapters": 1, "slides": 44, "folder": "lectures/ai/roles", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/roles.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:prompting"], "audience": ["audiences:developers"]}, {"name": "Skills", "type": "lecture", "chapters": 1, "slides": 51, "folder": "lectures/ai/skills", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/skills.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm"], "audience": ["audiences:developers"]}, {"name": "Skills Advanced", "type": "lecture", "chapters": 1, "slides": 43, "folder": "lectures/ai/skills_advanced", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/skills_advanced.pdf", "level": "advanced", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm"], "audience": ["audiences:developers"]}, {"name": "Tools", "type": "lecture", "chapters": 1, "slides": 41, "folder": "lectures/ai/tools", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/tools.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:tools"], "audience": ["audiences:developers"]}, {"name": "Workflows", "type": "lecture", "chapters": 1, "slides": 47, "folder": "lectures/ai/workflows", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/workflows.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:workflows", "concepts:agents", "concepts:llm", "concepts:orchestration"], "audience": ["audiences:developers"]}, {"name": "Writing Agents", "type": "lecture", "chapters": 1, "slides": 100, "folder": "lectures/ai/writing_agents", "folder_label": "Ai", "pdf": "/teaching-slides/marp/lectures/ai/writing_agents.pdf", "level": "intermediate", "category": "ai", "duration_hours": 0, "tags": ["concepts:ai", "concepts:agents", "concepts:llm", "concepts:tools"], "audience": ["audiences:developers"]}, {"name": "Idempotency", "type": "lecture", "chapters": 1, "slides": 55, "folder": "lectures/architecting/idempotency", "folder_label": "Architecting", "pdf": "/teaching-slides/marp/lectures/architecting/idempotency.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 0, "tags": ["concepts:idempotency", "concepts:api-design", "concepts:reliability"], "audience": ["audiences:developers"]}, {"name": "Senior Level Development", "type": "lecture", "chapters": 1, "slides": 24, "folder": "lectures/architecting/senior-level-development", "folder_label": "Architecting", "pdf": "/teaching-slides/marp/lectures/architecting/senior-level-development.pdf", "level": "advanced", "category": "architecture", "duration_hours": 0, "tags": ["concepts:architecture", "practices:leadership", "practices:code-quality"], "audience": ["audiences:developers", "audiences:architects", "audiences:managers"]}, {"name": "Solid", "type": "lecture", "chapters": 1, "slides": 44, "folder": "lectures/architecting/solid", "folder_label": "Architecting", "pdf": "/teaching-slides/marp/lectures/architecting/solid.pdf", "level": "intermediate", "category": "architecture", "duration_hours": 0, "tags": ["concepts:oop", "concepts:design-patterns", "concepts:architecture"], "audience": ["audiences:developers"]}, {"name": "Spark Internals", "type": "lecture", "chapters": 1, "slides": 10, "folder": "lectures/big_data/spark-internals", "folder_label": "Big Data", "pdf": "/teaching-slides/marp/lectures/big_data/spark-internals.pdf", "level": "advanced", "category": "big-data", "duration_hours": 0, "tags": ["tools:spark", "data-and-ai:big-data", "concepts:distributed-systems"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Spark Notebooks", "type": "lecture", "chapters": 1, "slides": 27, "folder": "lectures/big_data/spark-notebooks", "folder_label": "Big Data", "pdf": "/teaching-slides/marp/lectures/big_data/spark-notebooks.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 0, "tags": ["tools:spark", "tools:jupyter", "data-and-ai:big-data"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Spark Reports", "type": "lecture", "chapters": 1, "slides": 49, "folder": "lectures/big_data/spark-reports", "folder_label": "Big Data", "pdf": "/teaching-slides/marp/lectures/big_data/spark-reports.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 0, "tags": ["tools:spark", "data-and-ai:big-data", "practices:monitoring"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Spark Scala Datasets", "type": "lecture", "chapters": 1, "slides": 37, "folder": "lectures/big_data/spark-scala-datasets", "folder_label": "Big Data", "pdf": "/teaching-slides/marp/lectures/big_data/spark-scala-datasets.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 0, "tags": ["tools:spark", "languages:scala", "data-and-ai:big-data"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Spark Ui", "type": "lecture", "chapters": 1, "slides": 39, "folder": "lectures/big_data/spark-ui", "folder_label": "Big Data", "pdf": "/teaching-slides/marp/lectures/big_data/spark-ui.pdf", "level": "intermediate", "category": "big-data", "duration_hours": 0, "tags": ["tools:spark", "data-and-ai:big-data", "practices:monitoring", "practices:debugging"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Gcc Optimizations", "type": "lecture", "chapters": 1, "slides": 22, "folder": "lectures/build_systems/gcc-optimizations", "folder_label": "Build Systems", "pdf": "/teaching-slides/marp/lectures/build_systems/gcc-optimizations.pdf", "level": "advanced", "category": "build-systems", "duration_hours": 0, "tags": ["tools:gcc", "concepts:performance", "concepts:compilation"], "audience": ["audiences:developers"]}, {"name": "Aws Ecs", "type": "lecture", "chapters": 1, "slides": 34, "folder": "lectures/cloud/aws-ecs", "folder_label": "Cloud", "pdf": "/teaching-slides/marp/lectures/cloud/aws-ecs.pdf", "level": "intermediate", "category": "cloud", "duration_hours": 0, "tags": ["infrastructure:cloud", "infrastructure:aws", "practices:containers"], "audience": ["audiences:developers", "audiences:sysadmins", "audiences:devops"]}, {"name": "Aws Lambda", "type": "lecture", "chapters": 1, "slides": 34, "folder": "lectures/cloud/aws-lambda", "folder_label": "Cloud", "pdf": "/teaching-slides/marp/lectures/cloud/aws-lambda.pdf", "level": "intermediate", "category": "cloud", "duration_hours": 0, "tags": ["infrastructure:cloud", "infrastructure:aws", "practices:serverless"], "audience": ["audiences:developers", "audiences:devops", "audiences:architects"]}, {"name": "Azure Boards", "type": "lecture", "chapters": 1, "slides": 27, "folder": "lectures/cloud/azure-boards", "folder_label": "Cloud", "pdf": "/teaching-slides/marp/lectures/cloud/azure-boards.pdf", "level": "beginner", "category": "cloud", "duration_hours": 0, "tags": ["tools:azure", "practices:project-management", "practices:agile"], "audience": ["audiences:developers", "audiences:managers", "audiences:devops"]}, {"name": "Acid", "type": "lecture", "chapters": 1, "slides": 33, "folder": "lectures/databases/acid", "folder_label": "Databases", "pdf": "/teaching-slides/marp/lectures/databases/acid.pdf", "level": "intermediate", "category": "database", "duration_hours": 0, "tags": ["concepts:databases", "concepts:transactions", "concepts:data-integrity"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Data Formats", "type": "lecture", "chapters": 1, "slides": 63, "folder": "lectures/databases/data_formats", "folder_label": "Databases", "pdf": "/teaching-slides/marp/lectures/databases/data_formats.pdf", "level": "beginner", "category": "database", "duration_hours": 0, "tags": ["concepts:data-formats", "concepts:serialization", "concepts:databases"], "audience": ["audiences:developers", "audiences:data-engineers", "audiences:data-scientists"]}, {"name": "Nosql Database Fundamentals", "type": "lecture", "chapters": 1, "slides": 56, "folder": "lectures/databases/nosql-database-fundamentals", "folder_label": "Databases", "pdf": "/teaching-slides/marp/lectures/databases/nosql-database-fundamentals.pdf", "level": "intermediate", "category": "database", "duration_hours": 0, "tags": ["data-and-ai:nosql", "concepts:databases", "concepts:data-modeling"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Sql Database Fundamentals", "type": "lecture", "chapters": 1, "slides": 53, "folder": "lectures/databases/sql-database-fundamentals", "folder_label": "Databases", "pdf": "/teaching-slides/marp/lectures/databases/sql-database-fundamentals.pdf", "level": "beginner", "category": "database", "duration_hours": 0, "tags": ["languages:sql", "concepts:databases", "concepts:data-modeling"], "audience": ["audiences:developers", "audiences:data-engineers"]}, {"name": "Devops Slides", "type": "lecture", "chapters": 1, "slides": 28, "folder": "lectures/devops/devops-slides", "folder_label": "Devops", "pdf": "/teaching-slides/marp/lectures/devops/devops-slides.pdf", "level": "beginner", "category": "devops", "duration_hours": 0, "tags": ["practices:devops", "practices:ci-cd", "concepts:automation"], "audience": ["audiences:developers", "audiences:devops", "audiences:managers"]}, {"name": "Eks", "type": "lecture", "chapters": 1, "slides": 12, "folder": "lectures/devops/eks", "folder_label": "Devops", "pdf": "/teaching-slides/marp/lectures/devops/eks.pdf", "level": "advanced", "category": "devops", "duration_hours": 0, "tags": ["tools:kubernetes", "infrastructure:aws", "infrastructure:containers"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Logstash", "type": "lecture", "chapters": 1, "slides": 49, "folder": "lectures/devops/logstash", "folder_label": "Devops", "pdf": "/teaching-slides/marp/lectures/devops/logstash.pdf", "level": "intermediate", "category": "devops", "duration_hours": 0, "tags": ["tools:logstash", "tools:elk", "practices:logging", "practices:monitoring"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Microcontroller Bootloader", "type": "lecture", "chapters": 1, "slides": 47, "folder": "lectures/embedded/microcontroller-bootloader", "folder_label": "Embedded", "pdf": "/teaching-slides/marp/lectures/embedded/microcontroller-bootloader.pdf", "level": "advanced", "category": "embedded", "duration_hours": 0, "tags": ["concepts:embedded", "concepts:firmware", "concepts:bootloader"], "audience": ["audiences:developers"]}, {"name": "Git Workflows", "type": "lecture", "chapters": 1, "slides": 41, "folder": "lectures/git/git-workflows", "folder_label": "Git", "pdf": "/teaching-slides/marp/lectures/git/git-workflows.pdf", "level": "intermediate", "category": "version-control", "duration_hours": 0, "tags": ["tools:git", "concepts:version-control", "practices:collaboration"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "C++17", "type": "lecture", "chapters": 1, "slides": 47, "folder": "lectures/languages/c++17", "folder_label": "Languages", "pdf": "/teaching-slides/marp/lectures/languages/c++17.pdf", "level": "intermediate", "category": "language", "duration_hours": 0, "tags": ["languages:c++", "concepts:programming"], "audience": ["audiences:developers"]}, {"name": "Numpy", "type": "lecture", "chapters": 1, "slides": 30, "folder": "lectures/languages/python/numpy", "folder_label": "Languages / Python", "pdf": "/teaching-slides/marp/lectures/languages/python/numpy.pdf", "level": "intermediate", "category": "language", "duration_hours": 0, "tags": ["languages:python", "concepts:data-science", "concepts:performance", "concepts:numerical-computing", "tools:numpy"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Pandas", "type": "lecture", "chapters": 1, "slides": 29, "folder": "lectures/languages/python/pandas", "folder_label": "Languages / Python", "pdf": "/teaching-slides/marp/lectures/languages/python/pandas.pdf", "level": "intermediate", "category": "language", "duration_hours": 0, "tags": ["languages:python", "concepts:data-science", "concepts:dataframes", "tools:pandas"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Polars", "type": "lecture", "chapters": 1, "slides": 40, "folder": "lectures/languages/python/polars", "folder_label": "Languages / Python", "pdf": "/teaching-slides/marp/lectures/languages/python/polars.pdf", "level": "intermediate", "category": "language", "duration_hours": 0, "tags": ["languages:python", "concepts:data-science", "concepts:dataframes", "concepts:performance", "tools:polars"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "R To Python", "type": "lecture", "chapters": 1, "slides": 49, "folder": "lectures/languages/r-to-python", "folder_label": "Languages", "pdf": "/teaching-slides/marp/lectures/languages/r-to-python.pdf", "level": "intermediate", "category": "language", "duration_hours": 0, "tags": ["languages:python", "languages:r", "concepts:programming", "concepts:data-science"], "audience": ["audiences:developers", "audiences:data-scientists"]}, {"name": "Scala Basics", "type": "lecture", "chapters": 1, "slides": 52, "folder": "lectures/languages/scala-basics", "folder_label": "Languages", "pdf": "/teaching-slides/marp/lectures/languages/scala-basics.pdf", "level": "beginner", "category": "language", "duration_hours": 0, "tags": ["languages:scala", "concepts:programming", "concepts:functional-programming"], "audience": ["audiences:developers"]}, {"name": "Iouring", "type": "lecture", "chapters": 1, "slides": 42, "folder": "lectures/operating_systems/iouring", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/iouring.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:io", "concepts:linux-kernel", "concepts:performance"], "audience": ["audiences:developers"]}, {"name": "Isolation In Computing", "type": "lecture", "chapters": 1, "slides": 54, "folder": "lectures/operating_systems/isolation-in-computing", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/isolation-in-computing.pdf", "level": "intermediate", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:isolation", "concepts:security", "concepts:virtualization", "infrastructure:containers"], "audience": ["audiences:developers", "audiences:devops"]}, {"name": "Linux Io", "type": "lecture", "chapters": 1, "slides": 11, "folder": "lectures/operating_systems/linux-io", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/linux-io.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:io", "concepts:linux-kernel", "concepts:filesystems"], "audience": ["audiences:developers"]}, {"name": "Linux Kernel And Interrupts", "type": "lecture", "chapters": 1, "slides": 42, "folder": "lectures/operating_systems/linux-kernel-and-interrupts", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/linux-kernel-and-interrupts.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:linux-kernel", "concepts:interrupts", "concepts:drivers"], "audience": ["audiences:developers"]}, {"name": "Virtio", "type": "lecture", "chapters": 1, "slides": 28, "folder": "lectures/operating_systems/virtio", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/virtio.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:virtualization", "concepts:linux-kernel", "concepts:io"], "audience": ["audiences:developers"]}, {"name": "Writing Netfilter Modules", "type": "lecture", "chapters": 1, "slides": 14, "folder": "lectures/operating_systems/writing-netfilter-modules", "folder_label": "Operating Systems", "pdf": "/teaching-slides/marp/lectures/operating_systems/writing-netfilter-modules.pdf", "level": "advanced", "category": "operating-systems", "duration_hours": 0, "tags": ["concepts:linux-kernel", "concepts:networking", "concepts:security"], "audience": ["audiences:developers"]}];
/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage under a single shared
 * key. All sibling sites on the same origin (veltzer.org/*) share the
 * theme: pick a theme on one, navigate to another, and the choice
 * follows you.
 *
 * The default theme is "azure" (set in themes.css). Override at runtime
 * with defaultTheme if a specific app wants a different starting theme:
 *   initThemeSwitcher({ defaultTheme: "midnight" });
 */
const THEME_STORAGE_KEY = "veltzer-site-theme";

function initThemeSwitcher(options) {
    options = options || {};
    const defaultTheme = options.defaultTheme || "azure";
    const sel = document.getElementById("theme-select");
    if (!sel) return;
    const saved = localStorage.getItem(THEME_STORAGE_KEY) || defaultTheme;
    const isMaterial = sel.tagName.toLowerCase() === "md-outlined-select"
        || sel.tagName.toLowerCase() === "md-filled-select";

    function setSelValue(name) {
        if (isMaterial) {
            // For <md-outlined-select> we have to flip the `selected`
            // attribute on the matching <md-select-option> child, then
            // poke the host so it reflects the new selection.
            const opts = sel.querySelectorAll("md-select-option");
            opts.forEach(function(o) {
                if (o.value === name) {
                    o.setAttribute("selected", "");
                    o.selected = true;
                } else {
                    o.removeAttribute("selected");
                    o.selected = false;
                }
            });
            sel.value = name;
        } else {
            sel.value = name;
        }
    }

    function applyTheme(name) {
        document.documentElement.setAttribute("data-theme", name);
        setSelValue(name);
        localStorage.setItem(THEME_STORAGE_KEY, name);
    }

    sel.addEventListener("change", function() {
        applyTheme(sel.value);
    });

    // Pick up changes made by sibling tabs/sites on the same origin.
    window.addEventListener("storage", function(e) {
        if (e.key === THEME_STORAGE_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    applyTheme(saved);
}

/* global DATA */
const ICON_PDF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><text x="12" y="17" text-anchor="middle" font-size="6" fill="currentColor" stroke="none" font-weight="bold">PDF</text></svg>';

let currentFolder = "";

const breadcrumbEl = document.getElementById("breadcrumb");
const subfoldersEl = document.getElementById("subfolders");
const searchEl = document.getElementById("search");
const levelEl = document.getElementById("filter-level");
const categoryEl = document.getElementById("filter-category");
const typeEl = document.getElementById("filter-type");
const tagEl = document.getElementById("filter-tag");
const audienceEl = document.getElementById("filter-audience");
const durationEl = document.getElementById("filter-duration");
const numbersEl = document.getElementById("show-numbers");
const sort1El = document.getElementById("sort-primary");
const sort1DirEl = document.getElementById("sort-primary-dir");
const sort2El = document.getElementById("sort-secondary");
const sort2DirEl = document.getElementById("sort-secondary-dir");
const resultsEl = document.getElementById("results");
const totalEl = document.getElementById("total-count");

// Compute duration days
DATA.forEach(e => {
    e.dh = e.duration_hours || 0;
    e.duration_days = e.dh ? Math.round(e.dh / 8) : 0;
});

// Populate duration filter (md-select-option for @material/web variant)
const ALL_DURATION_DAYS = [...new Set(DATA.map(e => e.duration_days).filter(d => d > 0))].sort((a, b) => a - b);
durationEl.innerHTML = '<md-select-option value="" selected><div slot="headline">All durations</div></md-select-option>' +
    ALL_DURATION_DAYS.map(d => '<md-select-option value="' + d + '"><div slot="headline">' + d + (d === 1 ? " day" : " days") + " / " + (d * 8) + "h</div></md-select-option>").join("");

// Update select labels with counts (the .label property is the floating
// label on <md-outlined-select>; there are no <label for> elements).
levelEl.label = "Level (" + new Set(DATA.map(e => e.level).filter(Boolean)).size + ")";
categoryEl.label = "Category (" + new Set(DATA.map(e => e.category).filter(Boolean)).size + ")";
typeEl.label = "Type (" + new Set(DATA.map(e => e.type).filter(Boolean)).size + ")";
tagEl.label = "Tag (" + new Set(DATA.flatMap(e => e.tags)).size + ")";
durationEl.label = "Duration (" + ALL_DURATION_DAYS.length + ")";
audienceEl.label = "Audience (" + new Set(DATA.flatMap(e => e.audience)).size + ")";

function navigateFolder(folder) {
    currentFolder = folder;
    history.pushState(null, "", folder ? "#folder=" + encodeURIComponent(folder) : "#");
    render();
    window.scrollTo(0, 0);
}

function renderBreadcrumb() {
    if (!currentFolder) {
        breadcrumbEl.innerHTML = '<span class="breadcrumb-current">All Items</span>';
        return;
    }
    const parts = currentFolder.split("/");
    let html = '<a href="#" onclick="navigateFolder(\'\'); return false;">All Items</a>';
    for (let i = 0; i < parts.length; i++) {
        const path = parts.slice(0, i + 1).join("/");
        const label = parts[i].replace(/_/g, " ").replace(/-/g, " ");
        html += '<span class="breadcrumb-sep">&gt;</span>';
        if (i === parts.length - 1) {
            html += '<span class="breadcrumb-current">' + label + '</span>';
        } else {
            html += '<a href="#" onclick="navigateFolder(\'' + path.replace(/'/g, "\\'") + '\'); return false;">' + label + '</a>';
        }
    }
    breadcrumbEl.innerHTML = html;
}

function getSubfolders(folder, entries) {
    const prefix = folder ? folder + "/" : "";
    const subs = new Map();
    for (const e of entries) {
        const path = e.folder;
        if (prefix && !path.startsWith(prefix)) continue;
        const rest = prefix ? path.substring(prefix.length) : path;
        if (!rest) continue;
        const slash = rest.indexOf("/");
        if (slash === -1) continue;
        const sub = rest.substring(0, slash);
        subs.set(sub, (subs.get(sub) || 0) + 1);
    }
    return [...subs.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

function renderSubfolders(filtered) {
    const subs = getSubfolders(currentFolder, filtered);
    if (subs.length === 0) {
        subfoldersEl.innerHTML = "";
        return;
    }
    subfoldersEl.innerHTML = subs.map(function(s) {
        var name = s[0];
        var count = s[1];
        var path = currentFolder ? currentFolder + "/" + name : name;
        var label = name.replace(/_/g, " ").replace(/-/g, " ");
        return '<a class="subfolder-card" href="#" onclick="navigateFolder(\'' +
            path.replace(/'/g, "\\'") + '\'); return false;">' +
            label + ' <span class="subfolder-count">(' + count + ')</span></a>';
    }).join("");
}

function render() {
    const search = (searchEl.value || "").toLowerCase();
    const level = levelEl.value || "";
    const category = categoryEl.value || "";
    const type = typeEl.value || "";
    const tag = tagEl.value || "";
    const audience = audienceEl.value || "";
    const duration = durationEl.value || "";
    const sort1 = sort1El.value || "folder";
    const sort1Dir = (sort1DirEl.value || "asc") === "asc" ? 1 : -1;
    const sort2 = sort2El.value || "name";
    const sort2Dir = (sort2DirEl.value || "asc") === "asc" ? 1 : -1;

    renderBreadcrumb();

    const filtered = DATA.filter(e => {
        if (currentFolder) {
            if (!e.folder.startsWith(currentFolder + "/") && e.folder !== currentFolder) return false;
        }
        if (search && !e.name.toLowerCase().includes(search)) return false;
        if (level && e.level !== level) return false;
        if (category && e.category !== category) return false;
        if (type && e.type !== type) return false;
        if (tag && !e.tags.includes(tag)) return false;
        if (audience && !e.audience.includes(audience)) return false;
        if (duration && e.duration_days !== parseInt(duration)) return false;
        return true;
    });

    const totalChapters = filtered.reduce((s, e) => s + (e.chapters || 0), 0);
    const totalSlides = filtered.reduce((s, e) => s + (e.slides || 0), 0);
    const nCourses = filtered.filter(e => e.type === "course").length;
    const nLectures = filtered.filter(e => e.type === "lecture").length;
    totalEl.innerHTML = nCourses + " courses, " + nLectures + " lectures, " +
        '<span class="stat-chapters">' + totalChapters + " chapters</span>, " +
        '<span class="stat-slides">' + totalSlides + " slides</span>";
    renderSubfolders(filtered);

    const LEVEL_ORDER = {beginner: 0, intermediate: 1, advanced: 2};
    const getVal = (e, key) => {
        if (key === "name") return e.name;
        if (key === "slides") return e.slides || 0;
        if (key === "chapters") return e.chapters || 0;
        if (key === "folder") { const p = e.folder.split("/"); return p.length > 1 ? p.slice(0, -1).join("/") : ""; }
        if (key === "level") return LEVEL_ORDER[e.level] ?? 3;
        if (key === "category") return e.category || "";
        if (key === "duration") return e.dh || 0;
        return e[key];
    };

    const getLabel = (e, key) => {
        if (key === "folder") {
            const parts = e.folder.split("/");
            if (parts.length <= 1) return "Root";
            return parts.slice(0, -1).map(p => p.replace(/_/g, " ").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase())).join(" / ");
        }
        if (key === "level") return (e.level || "No Level").charAt(0).toUpperCase() + (e.level || "No Level").slice(1);
        if (key === "category") return (e.category || "No Category").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        if (key === "duration") return e.dh ? e.duration_days + "d / " + e.dh + "h" : "No Duration";
        if (key === "slides") return e.slides + " slides";
        if (key === "chapters") return e.chapters + " chapters";
        if (key === "name") return "All Items";
        return "";
    };

    filtered.sort((a, b) => {
        const v1a = getVal(a, sort1);
        const v1b = getVal(b, sort1);
        if (v1a !== v1b) {
            const res = (typeof v1a === "string") ? v1a.localeCompare(v1b) : v1a - v1b;
            return res * sort1Dir;
        }
        const v2a = getVal(a, sort2);
        const v2b = getVal(b, sort2);
        if (v2a !== v2b) {
            const res = (typeof v2a === "string") ? v2a.localeCompare(v2b) : v2a - v2b;
            return res * sort2Dir;
        }
        return a.name.localeCompare(b.name);
    });

    const groups = [];
    let lastHeader = null;
    for (const item of filtered) {
        const h = getLabel(item, sort1);
        const folderKey = sort1 === "folder" ? getVal(item, "folder") : "";
        if (h !== lastHeader) {
            groups.push({ label: h, folderKey: folderKey, items: [] });
            lastHeader = h;
        }
        groups[groups.length - 1].items.push(item);
    }

    let html = "";
    if (groups.length === 0) {
        html = '<p class="no-results">No items match the current filters.</p>';
    }
    // <md-switch> exposes .selected, not .checked. Fall back to .checked
    // pre-upgrade so the first render works.
    const showNumbers = numbersEl.selected ?? numbersEl.checked ?? false;
    let globalNum = 0;
    for (const group of groups) {
        const groupChapters = group.items.reduce((s, e) => s + (e.chapters || 0), 0);
        const groupSlides = group.items.reduce((s, e) => s + (e.slides || 0), 0);
        let headerLabel = group.label;
        if (group.folderKey) {
            const fParts = group.folderKey.split("/");
            headerLabel = fParts.map((p, idx) => {
                const path = fParts.slice(0, idx + 1).join("/");
                const label = p.replace(/_/g, " ").replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
                return '<a href="#" onclick="navigateFolder(\'' + path.replace(/'/g, "\\'") + '\'); return false;">' + label + '</a>';
            }).join(' <span class="breadcrumb-sep">/</span> ');
        }
        const gc = group.items.filter(e => e.type === "course").length;
        const gl = group.items.filter(e => e.type === "lecture").length;
        const groupLabel = [gc ? gc + " courses" : "", gl ? gl + " lectures" : ""].filter(Boolean).join(", ");
        html += '<h2>' + headerLabel +
            ' <span class="count">(' + groupLabel + ', ' +
            '<span class="stat-chapters">' + groupChapters + ' chapters</span>, ' +
            '<span class="stat-slides">' + groupSlides + ' slides</span>)</span></h2><ul>';
        for (let i = 0; i < group.items.length; i++) {
            globalNum++;
            const item = group.items[i];
            const numPrefix = showNumbers ? '<span class="course-number">' + globalNum + ".</span> " : "";
            const nameHtml = item.pdf ? '<a href="' + item.pdf + '" target="_blank">' + item.name + "</a>" : "<span>" + item.name + "</span>";
            const typeBadge = '<md-assist-chip class="chip-type chip-type-' + item.type + '" label="' + item.type + '"></md-assist-chip>';
            const levelBadge = item.level ? '<md-assist-chip class="chip-level chip-level-' + item.level + '" label="' + item.level + '"></md-assist-chip>' : "";
            let db = "";
            if (item.dh) {
                db = item.duration_days + "d / " + item.dh + "h";
            }
            const durationBadge = db ? '<md-assist-chip class="chip-duration" label="' + db + '"></md-assist-chip>' : "";
            const chaptersBadge = item.chapters ? '<md-assist-chip class="chip-chapters" label="' + item.chapters + ' ch"></md-assist-chip>' : "";
            const slidesBadge = item.slides ? '<md-assist-chip class="chip-slides" label="' + item.slides + ' sl"></md-assist-chip>' : "";
            const pdfLink = item.pdf ? '<a class="dl-icon" href="' + item.pdf + '" download title="Download PDF">' + ICON_PDF + "</a>" : "";
            html += "<li>" + numPrefix + nameHtml + typeBadge + levelBadge + durationBadge + chaptersBadge + slidesBadge + " " + pdfLink + "</li>";
        }
        html += "</ul>";
    }
    resultsEl.innerHTML = html;
}

// Autocomplete
const acList = document.getElementById("autocomplete-list");
let acIndex = -1;

function updateAutocomplete() {
    const query = searchEl.value.toLowerCase();
    acIndex = -1;
    if (query.length < 2) {
        acList.classList.remove("visible");
        return;
    }
    const matches = DATA.filter(e => e.name.toLowerCase().includes(query)).slice(0, 10);
    if (matches.length === 0) {
        acList.classList.remove("visible");
        return;
    }
    acList.innerHTML = matches.map((m, i) =>
        '<div class="autocomplete-item" data-index="' + i + '">' +
        m.name + '<span class="ac-folder">' + m.folder_label + '</span></div>'
    ).join("");
    acList.classList.add("visible");
}

acList.addEventListener("mousedown", function(ev) {
    var item = ev.target.closest(".autocomplete-item");
    if (item) {
        acList.classList.remove("visible");
        var idx = parseInt(item.dataset.index);
        var query = searchEl.value.toLowerCase();
        var matches = DATA.filter(e => e.name.toLowerCase().includes(query));
        if (matches[idx]) {
            searchEl.value = matches[idx].name;
            render();
        }
    }
});

searchEl.addEventListener("keydown", function(ev) {
    var items = acList.querySelectorAll(".autocomplete-item");
    if (!acList.classList.contains("visible") || items.length === 0) return;
    if (ev.key === "ArrowDown") {
        ev.preventDefault();
        acIndex = Math.min(acIndex + 1, items.length - 1);
    } else if (ev.key === "ArrowUp") {
        ev.preventDefault();
        acIndex = Math.max(acIndex - 1, 0);
    } else if (ev.key === "Enter" && acIndex >= 0) {
        ev.preventDefault();
        acList.classList.remove("visible");
        var query = searchEl.value.toLowerCase();
        var matches = DATA.filter(e => e.name.toLowerCase().includes(query));
        if (matches[acIndex]) {
            searchEl.value = matches[acIndex].name;
            render();
        }
        return;
    } else if (ev.key === "Escape") {
        acList.classList.remove("visible");
        return;
    } else {
        return;
    }
    items.forEach(function(el, i) {
        el.classList.toggle("active", i === acIndex);
    });
});

searchEl.addEventListener("blur", function() {
    setTimeout(function() { acList.classList.remove("visible"); }, 150);
});

searchEl.addEventListener("input", function() {
    updateAutocomplete();
    render();
});
levelEl.addEventListener("change", render);
categoryEl.addEventListener("change", render);
typeEl.addEventListener("change", render);
tagEl.addEventListener("change", render);
audienceEl.addEventListener("change", render);
durationEl.addEventListener("change", render);
numbersEl.addEventListener("change", render);
sort1El.addEventListener("change", render);
sort1DirEl.addEventListener("change", render);
sort2El.addEventListener("change", render);
sort2DirEl.addEventListener("change", render);

window.addEventListener("popstate", function() {
    var hash = location.hash;
    if (hash && hash.startsWith("#folder=")) {
        currentFolder = decodeURIComponent(hash.substring(8));
    } else {
        currentFolder = "";
    }
    render();
});

// Wait for @material/web custom elements to upgrade before we read .value
// from the form controls. Without this, render() fires while the elements
// are still inert and .value is undefined.
(window.__mdReady || Promise.resolve()).then(function() {
    if (location.hash && location.hash.startsWith("#folder=")) {
        currentFolder = decodeURIComponent(location.hash.substring(8));
    }
    render();
    initThemeSwitcher();
});

</script>
