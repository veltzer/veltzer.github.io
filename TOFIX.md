# TOFIX

The full code review of 2026-11-15 (every script, test, template, stylesheet,
frontend file, config file and document; not the blog posts or the vendored
libraries) was fixed the same day, and so were the items that needed a
decision. The findings and their fixes are in the git history of this file and
in that day's commits. What is left needs a change outside this repository,
or was left alone on purpose.

## Needs a change elsewhere

- **`config/project.lua`** is read by nothing in this repository, but it has
  a consumer outside it: `rsmultigit gh sync-metadata` reads it for the
  GitHub description and topics. (`.luacheckrc`, which only configured a
  luacheck processor that does not run here, was removed on 2026-11-19.)

## Left alone on purpose

- **Movie "with" names** stay in `static/data/video_features.json.gz` and in
  `data/yaml/video_features.yaml`; the page does not show them
  (`showPeople: false`). Decided 2026-11-15.
- **`scripts/build_collection_css.sh` fetches `tailwindcss@3` with `npx`**
  at run time, by hand, outside the build: pinning it further goes against
  the no-pins rule, and bringing it into the build would add Node to CI.
- **`/keys.js` on the calendar page carries no `?v=`**: the page is markdown
  and has no access to the template's version string. The file changes only
  when the key is rotated.
- **The three imported app pages** (animations, slides, syllabi) keep the
  upstream sites' `<style>` blocks in the body: `import_teaching.py`
  generates them that way, and the tidy and vnu checks exclude them.
