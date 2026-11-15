# TOFIX

The full code review of 2026-11-15 (every script, test, template, stylesheet,
frontend file, config file and document; not the blog posts or the vendored
libraries) was fixed the same day. The findings and their fixes are in the git
history of this file and in that day's commit. What is left is below: each
item needs a decision or a change outside this repository.

## Needs a decision

- **Movie "with" names are still published.** The plugins now honour
  `showPeople: false` (`templates/data_collection.html`), so no page shows
  them, but 8 of the 65 entries in `static/data/video_features.json.gz` carry
  the names, and `data/yaml/video_features.yaml` in this public repository
  does too. Dropping `with` in `scripts/copy_data.py` would keep them out of
  the shipped JSON only; out of the repository is a larger change.
- **Rendered HTML is not validated.** The `itidy` processor matched no file
  (`static/` has no `.html`) and was removed. Pointed at `_site/` it gave
  6000+ warnings on a correct site: every Hebrew tag URL, `data-*`
  attributes, the custom elements of the imported teaching pages. A check
  that would have caught the nested `<main>` needs an HTML5 validator, or a
  tidy configuration, chosen deliberately.
- **`plugin-concerts.js` and `plugin-museums.js` are on no page**, since the
  concert and museum lists are private by decision, yet their `app_concerts_*`
  and `app_museums_*` strings are inlined into every collection page along
  with every other `app_` key. Either delete the two plugins and their
  strings, or have the template inline only the strings of the page's
  plugins (the key prefixes do not match the plugin keys, so that needs a
  mapping).
- **`manage_api_key.py rotate` writes the new key into `static/keys.js`
  whatever `--pass-path` says.** Right for the calendar key, the only key
  there is; wrong if the script is ever used for another.
- **The podcast scripts still re-wrap hand-wrapped strings.** With the shared
  ruamel setup a save with no edit keeps indentation, quoting and key order,
  but changes 94 lines of `data/yaml/podcasts.yaml` (4 of
  `video_youtube.yaml`): the long quoted descriptions wrapped by hand at
  uneven widths. Rewriting the file once through the scripts would make
  every later diff minimal.
- **`<style>` blocks remain in the body** of the calendar page, the two
  training pages and the imported animations page (their markdown carries
  them); the collection template's moved to `<head>`.
- **The language select navigates on `change`**, by design (`base.html`); in
  some browsers a keyboard user arrowing through the closed select is sent
  away at the first option.

## Needs a change elsewhere

- **rssite: link the post's JSON-LD to the Person.** `base.html` now gives
  the Person block an `@id` (`https://veltzer.org/#person`), but the
  `BlogPosting` rssite builds carries its own bare
  `{"@type": "Person", "name": ...}` author and no `image`
  (`page_json_ld` in rssite's `src/templates.rs`). It needs an author `@id`
  and an image option there.
- **`.oxlintrc.json:7` names a schema under `./node_modules/`**, which does
  not exist. The file is a fleet invariant (`oxlint-config` in
  `~/.config/rsmultigit/config.toml`), so the fix is fleet-wide.
- **`.luacheckrc` and `config/project.lua`** have no consumer in this
  repository; both are fleet files, left alone.
- **`scripts/build_collection_css.sh` fetches `tailwindcss@3` with `npx`**
  at run time, by hand, outside the build. Left as is: pinning it further
  goes against the no-pins rule, and bringing it into the build would add
  Node to CI.
- **`/keys.js` on the calendar page carries no `?v=`**: the page is markdown
  and has no access to the template's version string. The file changes only
  when the key is rotated.
