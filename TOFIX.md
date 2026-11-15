# TOFIX

The full code review of 2026-11-15 (every script, test, template, stylesheet,
frontend file, config file and document; not the blog posts or the vendored
libraries) was fixed the same day, and so were the items that needed a
decision. The findings and their fixes are in the git history of this file and
in that day's commits. What is left needs a change outside this repository,
or was left alone on purpose.

## Needs a change elsewhere

- **rssite: link the post's JSON-LD to the Person.** `base.html` gives the
  Person block an `@id` (`https://veltzer.org/#person`), but the
  `BlogPosting` rssite builds carries its own bare
  `{"@type": "Person", "name": ...}` author and no `image`
  (`page_json_ld` in rssite's `src/templates.rs`). It needs an author `@id`
  and an image option there.
- **rsconstruct / tidy: a nested `<main>` is not caught.** The `itidy` check
  now runs over the rendered `_site/`, but tidy 5.8's rules do not include
  HTML5's content model, so the defect that prompted the check would still
  pass. Catching it needs an HTML5 validator.
- **`.oxlintrc.json:7` names a schema under `./node_modules/`**, which does
  not exist. The file is a fleet invariant (`oxlint-config` in
  `~/.config/rsmultigit/config.toml`), so the fix is fleet-wide.
- **`.luacheckrc` and `config/project.lua`** have no consumer in this
  repository; both are fleet files.

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
  generates them that way, and the tidy check excludes them.
