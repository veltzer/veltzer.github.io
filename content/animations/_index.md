+++
title = "Teaching Animations"
template = "app.html"
+++

<style>
#app-animations {
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
#app-animations, [data-theme="azure"] #app-animations {
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
  --entity-1: #1976d2;
  --entity-2: #7b1fa2;
  --entity-3: #00897b;
  --entity-4: #c2185b;
  --gradient-start: #303fa1;
  --gradient-end: #526cfe;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
}
[data-theme="paper"] #app-animations {
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
  --entity-1: #5e6ba8;
  --entity-2: #7c4a8d;
  --entity-3: #3d8a7a;
  --entity-4: #a85a3e;
  --gradient-start: #2c2824;
  --gradient-end: #9b6b3e;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
}
[data-theme="midnight"] #app-animations {
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
  --entity-1: #7dd3fc;
  --entity-2: #c084fc;
  --entity-3: #5eead4;
  --entity-4: #fda4af;
  --gradient-start: #e8eaf0;
  --gradient-end: #6c8cff;
}
[data-theme="nord"] #app-animations {
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
  --entity-1: #81a1c1;
  --entity-2: #b48ead;
  --entity-3: #8fbcbb;
  --entity-4: #d08770;
  --gradient-start: #eceff4;
  --gradient-end: #88c0d0;
}
[data-theme="solarized"] #app-animations {
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
  --entity-1: #2aa198;
  --entity-2: #6c71c4;
  --entity-3: #cb4b16;
  --entity-4: #d33682;
  --gradient-start: #073642;
  --gradient-end: #268bd2;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
}
[data-theme="rosepine"] #app-animations {
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
  --entity-1: #9ccfd8;
  --entity-2: #31748f;
  --entity-3: #ebbcba;
  --entity-4: #f6c177;
  --gradient-start: #e0def4;
  --gradient-end: #c4a7e7;
}




@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
#app-animations {
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
#app-animations a {
  color: var(--accent);
  text-decoration: none;
  transition: color var(--transition);
}
#app-animations a:hover { color: var(--text-primary); text-decoration: underline; }
#app-animations hr {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 48px 0 16px 0;
}
#app-animations ::-webkit-scrollbar { width: 8px; }
#app-animations ::-webkit-scrollbar-track { background: var(--bg); }
#app-animations ::-webkit-scrollbar-thumb { background: var(--border); border-radius: var(--radius-xs); }
#app-animations ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }


@media (max-width: 700px) {
  body { padding: 20px 16px; }

}
#app-animations h1 {
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
#app-animations h2 {
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 32px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}
#app-animations h2 a { color: var(--accent); text-decoration: none; }
#app-animations h2 a:hover { color: var(--text-primary); }
#app-animations h2 .count { color: var(--text-muted); text-transform: none; letter-spacing: normal; font-weight: 400; }
#app-animations #total-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 400;
  margin: 0 0 28px 0;
  letter-spacing: 0.02em;
}
#app-animations .subtitle {
  color: var(--text-secondary);
  margin: 0 0 2rem 0;
}
#app-animations .count {
  color: var(--text-muted);
  font-size: 0.9em;
}
#app-animations .no-results {
  color: var(--text-muted);
  font-style: italic;
  padding: 40px 0;
  text-align: center;
}
#app-animations .build-info {
  font-size: 0.85em;
  opacity: 0.7;
  margin-top: 0.2em;
}
#app-animations .build-info code {
  background: transparent;
  padding: 0;
  font-size: 0.95em;
}


@media (max-width: 700px) {
  h1 { font-size: 1.5rem; }

}
#app-animations .header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 4px;
}
#app-animations #theme-select { flex-shrink: 0; }
#app-animations .filters {
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
#app-animations .filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}
#app-animations .filter-row-sort {
  grid-column: 1 / -1;
  flex-wrap: wrap;
}
#app-animations .filter-row label {
  font-weight: 500;
  font-size: 0.82rem;
  color: var(--text-secondary);
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
#app-animations select, #app-animations input[type="text"] {
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
#app-animations select:focus, #app-animations input[type="text"]:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
#app-animations input[type="text"] { width: 240px; }
#app-animations select { cursor: pointer; }
#app-animations .toggle-switch { position: relative; display: inline-block; width: 36px; height: 20px; vertical-align: middle; }
#app-animations .toggle-switch input { opacity: 0; width: 0; height: 0; }
#app-animations .toggle-slider {
  position: absolute; cursor: pointer; inset: 0;
  background: var(--border); border-radius: var(--radius-pill);
  transition: background var(--transition);
}
#app-animations .toggle-slider:before {
  content: ""; position: absolute;
  height: 14px; width: 14px; left: 3px; bottom: 3px;
  background: var(--text-secondary); border-radius: 50%;
  transition: transform var(--transition), background var(--transition);
}
#app-animations .toggle-switch input:checked + .toggle-slider { background: var(--accent); }
#app-animations .toggle-switch input:checked + .toggle-slider:before { transform: translateX(16px); background: var(--bg); }
#app-animations #breadcrumb { margin-bottom: 12px; font-size: 0.88rem; }
#app-animations #breadcrumb a { color: var(--accent); text-decoration: none; }
#app-animations #breadcrumb a:hover { color: var(--text-primary); }
#app-animations .breadcrumb-sep { color: var(--text-muted); margin: 0 6px; }
#app-animations .breadcrumb-current { font-weight: 600; color: var(--text-primary); }
#app-animations #subfolders { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
#app-animations #subfolders:empty { margin-bottom: 0; }
#app-animations .subfolder-card {
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
#app-animations .subfolder-card:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
  text-decoration: none;
}
#app-animations .subfolder-count { color: var(--text-muted); font-weight: 400; font-size: 0.82rem; }
#app-animations ul { list-style: none; padding: 0; margin: 0; }
#app-animations li {
  padding: 10px 16px;
  margin: 0;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  transition: background var(--transition);
}
#app-animations li:hover { background: var(--bg-elevated); }
#app-animations li.hidden { display: none; }
#app-animations li a {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition);
}
#app-animations li a:hover { color: var(--accent); }
#app-animations .level, #app-animations .chapters-badge, #app-animations .slides-badge, #app-animations .duration, #app-animations .tag, #app-animations .type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}
#app-animations .level-beginner { background: var(--accent-dim); color: var(--accent); opacity: 0.7; }
#app-animations .level-intermediate { background: var(--accent-dim); color: var(--accent); opacity: 0.85; }
#app-animations .level-advanced { background: var(--accent-dim); color: var(--accent); }
#app-animations .tag { background: var(--accent-dim); color: var(--accent); }
#app-animations .chapters-badge { background: var(--accent-dim); color: var(--accent); opacity: 0.7; }
#app-animations .slides-badge { background: var(--accent-dim); color: var(--accent); }
#app-animations .duration { background: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border-subtle); }
#app-animations .type-badge { background: var(--success-dim); color: var(--success); text-transform: capitalize; }
#app-animations .type-course { background: var(--success-dim); color: var(--success); }
#app-animations .type-lecture { background: var(--warning-dim); color: var(--warning); }
#app-animations .course-number {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 400;
  min-width: 2.5em;
  display: inline-block;
}
#app-animations .stat-chapters { color: var(--text-secondary); font-weight: 600; }
#app-animations .stat-slides { color: var(--accent); font-weight: 600; }
#app-animations .dl-icon {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  color: var(--text-muted);
  transition: color var(--transition), transform var(--transition);
}
#app-animations .dl-icon:hover { color: var(--accent); transform: scale(1.15); }
#app-animations .dl-icon svg { width: 18px; height: 18px; }
#app-animations .autocomplete-wrap { position: relative; display: inline-block; }
#app-animations .autocomplete-list {
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
#app-animations .autocomplete-list.visible { display: block; }
#app-animations .autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background var(--transition);
}
#app-animations .autocomplete-item:hover, #app-animations .autocomplete-item.active { background: var(--bg-hover); }
#app-animations .autocomplete-item .ac-folder { color: var(--text-muted); font-size: 0.78rem; margin-left: 8px; }



@media (max-width: 700px) {
  .header-bar { flex-direction: column; gap: 10px; }
#app-animations .filters { grid-template-columns: 1fr; padding: 16px; }
#app-animations input[type="text"] { width: 100%; }
#app-animations li { padding: 8px 10px; }

}
#app-animations {
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
#app-animations md-outlined-text-field#search { width: 100%; }
#app-animations .header-bar md-outlined-select { width: auto; min-width: 220px; }
#app-animations #results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}
#app-animations .card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  cursor: pointer;
  transition: border-color var(--transition), transform var(--transition), background var(--transition);
}
#app-animations .card:hover {
  border-color: var(--accent);
  background: var(--bg-hover);
  transform: translateY(-2px);
}
#app-animations .card h3 { margin: 0 0 0.5rem 0; color: var(--accent); font-size: 1.15rem; }
#app-animations .card p { margin: 0; color: var(--text-secondary); font-size: 0.95rem; }
#app-animations .card .meta { margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-muted); }
#app-animations footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: center;
}
#app-animations footer a { color: var(--accent); text-decoration: none; }
#app-animations footer a:hover { text-decoration: underline; opacity: 0.85; }
#app-animations #player-toolbar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
#app-animations #back-btn {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.95rem;
}
#app-animations #back-btn:hover { border-color: var(--accent); color: var(--accent); }
#app-animations #player-title { margin: 0; font-size: 1.5rem; }
#app-animations .scene-block { margin-bottom: 2rem; }
#app-animations .scene-block h3 { margin: 0 0 0.75rem 0; color: var(--text-primary); font-size: 1.1rem; }
#app-animations .scene-block video {
  width: 100%;
  max-width: 100%;
  
  background: #000;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}
</style>

<div id="app-animations" class="app-root">
<div id="index-view">


<div class="filters">
<md-outlined-text-field id="search" label="Search" placeholder="Search by title..." autocomplete="off"></md-outlined-text-field>
</div>

<div id="results"></div>

<footer>
<p>Mark Veltzer &mdash; <a href="mailto:mark.veltzer@gmail.com">mark.veltzer@gmail.com</a> &mdash; <a href="https://github.com/veltzer/teaching-animations">source</a> &mdash; &copy; 2026</p>
</footer>
</div>

<div id="player-view" style="display:none">
<div id="player-toolbar">
<button id="back-btn">&larr; Back to index</button>
<h2 id="player-title"></h2>
</div>
<div id="player-content"></div>
</div>
</div>

<script type="module">
import "https://cdn.jsdelivr.net/npm/@material/web@2/all.js/+esm";
window.__mdReady = Promise.all([
  customElements.whenDefined("md-outlined-text-field"),
  customElements.whenDefined("md-outlined-select"),
  customElements.whenDefined("md-select-option"),
]);
</script>

<script>
const DATA = [{"slug": "bitcoin_ledger", "title": "Bitcoin Ledger", "description": "In this video, we will look at the heart of Bitcoin: its ledger. We will see what it is, who keeps it, and why it cannot easily be cheated.", "scenes": [{"label": "Animation", "path": "animations/bitcoin_ledger.mp4"}, {"label": "Summary", "path": "animations/bitcoin_ledger_summary.mp4"}]}, {"slug": "buffer_overflow", "title": "Buffer Overflow", "description": "A buffer overflow is what happens when a program writes past the end of an array. On the stack, that overwrites whatever sits next to the array — and what sits next to it can be very valuable.", "scenes": [{"label": "Animation", "path": "animations/buffer_overflow.mp4"}, {"label": "Summary", "path": "animations/buffer_overflow_summary.mp4"}]}, {"slug": "clock", "title": "Clock", "description": "Once a user program is running on the CPU, how does the operating system ever get control back? The answer is the timer interrupt.", "scenes": [{"label": "Animation", "path": "animations/clock.mp4"}, {"label": "Summary", "path": "animations/clock_summary.mp4"}]}, {"slug": "diffie_hellman", "title": "Diffie Hellman", "description": "How can two strangers, talking over a wire that anyone can read, agree on a secret key — without ever sending the key itself? The answer is Diffie-Hellman key exchange.", "scenes": [{"label": "Animation", "path": "animations/diffie_hellman.mp4"}, {"label": "Summary", "path": "animations/diffie_hellman_summary.mp4"}]}, {"slug": "fork", "title": "Fork", "description": "The fork system call creates a new process by duplicating the calling one. Two processes — the parent and the child — leave fork in nearly identical states. Almost. The return value is what tells them apart.", "scenes": [{"label": "Animation", "path": "animations/fork.mp4"}, {"label": "Summary", "path": "animations/fork_summary.mp4"}]}, {"slug": "mutex", "title": "Mutex", "description": "A mutex — short for mutual exclusion — is the simplest tool for keeping threads from stepping on each other. Only one thread holds the lock at a time. Everyone else waits.", "scenes": [{"label": "Animation", "path": "animations/mutex.mp4"}, {"label": "Summary", "path": "animations/mutex_summary.mp4"}]}, {"slug": "pipes", "title": "Pipes", "description": "A pipe is a fixed-size buffer inside the kernel with two file descriptors — one for writing, one for reading. The writer pours bytes in one end, the reader takes them out the other.", "scenes": [{"label": "Animation", "path": "animations/pipes.mp4"}, {"label": "Summary", "path": "animations/pipes_summary.mp4"}]}, {"slug": "race_condition", "title": "Race Condition", "description": "When two threads update the same variable at the same time, the result depends on exactly how their instructions are interleaved. This is called a race condition.", "scenes": [{"label": "Animation", "path": "animations/race_condition.mp4"}, {"label": "Summary", "path": "animations/race_condition_summary.mp4"}]}, {"slug": "stack_frame", "title": "Stack Frame", "description": "Every time a function is called, the CPU pushes a chunk of bookkeeping onto the stack — locals, the return address, the saved frame pointer. That chunk is the function's stack frame.", "scenes": [{"label": "Animation", "path": "animations/stack_frame.mp4"}, {"label": "Summary", "path": "animations/stack_frame_summary.mp4"}]}, {"slug": "swapping", "title": "Swapping", "description": "In this video, we will look at how operating systems use swapping to give programs the illusion of having more memory than the machine actually has.", "scenes": [{"label": "Animation", "path": "animations/swapping.mp4"}, {"label": "Summary", "path": "animations/swapping_summary.mp4"}]}, {"slug": "syscall", "title": "Syscall", "description": "In this video, we will look at how a system call works. We will use the read system call as our running example.", "scenes": [{"label": "Animation", "path": "animations/syscall.mp4"}, {"label": "Summary", "path": "animations/syscall_summary.mp4"}]}, {"slug": "tcp_handshake", "title": "Tcp Handshake", "description": "Before any data flows over a TCP connection, the two endpoints exchange three small packets to agree on starting sequence numbers and confirm they can both send and receive. This is the three-way handshake.", "scenes": [{"label": "Animation", "path": "animations/tcp_handshake.mp4"}, {"label": "Summary", "path": "animations/tcp_handshake_summary.mp4"}]}];
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

const indexView = document.getElementById("index-view");
const playerView = document.getElementById("player-view");
const playerTitle = document.getElementById("player-title");
const playerContent = document.getElementById("player-content");
const backBtn = document.getElementById("back-btn");
const results = document.getElementById("results");
const search = document.getElementById("search");

function render(filter) {
    const q = (filter || "").trim().toLowerCase();
    const visible = DATA.filter(entry => {
        if (!q) return true;
        return entry.title.toLowerCase().includes(q) ||
               entry.description.toLowerCase().includes(q) ||
               entry.slug.toLowerCase().includes(q);
    });

    results.innerHTML = "";
    if (visible.length === 0) {
        const empty = document.createElement("div");
        empty.className = "no-results";
        empty.textContent = "No animations match your search.";
        results.appendChild(empty);
        return;
    }

    for (const entry of visible) {
        const card = document.createElement("div");
        card.className = "card";
        card.addEventListener("click", () => openPlayer(entry));

        const h3 = document.createElement("h3");
        h3.textContent = entry.title;
        card.appendChild(h3);

        const p = document.createElement("p");
        p.textContent = entry.description;
        card.appendChild(p);

        const meta = document.createElement("div");
        meta.className = "meta";
        const sceneCount = entry.scenes.length;
        meta.textContent = sceneCount + " scene" + (sceneCount === 1 ? "" : "s");
        card.appendChild(meta);

        results.appendChild(card);
    }
}

function openPlayer(entry) {
    playerTitle.textContent = entry.title;
    playerContent.innerHTML = "";

    for (const scene of entry.scenes) {
        const block = document.createElement("div");
        block.className = "scene-block";

        const h3 = document.createElement("h3");
        h3.textContent = scene.label;
        block.appendChild(h3);

        const video = document.createElement("video");
        video.src = scene.path;
        video.controls = true;
        video.preload = "metadata";
        block.appendChild(video);

        playerContent.appendChild(block);
    }

    indexView.style.display = "none";
    playerView.style.display = "block";
    window.scrollTo(0, 0);
    location.hash = "#" + entry.slug;
}

function closePlayer() {
    for (const v of playerContent.querySelectorAll("video")) {
        v.pause();
    }
    playerView.style.display = "none";
    indexView.style.display = "block";
    if (location.hash) {
        history.pushState("", document.title, location.pathname);
    }
}

function handleHash() {
    const slug = location.hash.replace(/^#/, "");
    if (!slug) {
        closePlayer();
        return;
    }
    const entry = DATA.find(e => e.slug === slug);
    if (entry) {
        openPlayer(entry);
    }
}

backBtn.addEventListener("click", closePlayer);
search.addEventListener("input", () => render(search.value || ""));
window.addEventListener("hashchange", handleHash);

// Wait for @material/web to upgrade before reading search.value (which
// is undefined on <md-outlined-text-field> pre-upgrade).
(window.__mdReady || Promise.resolve()).then(function() {
    render("");
    handleHash();
    initThemeSwitcher();
});

</script>
