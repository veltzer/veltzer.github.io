+++
title = "Mark Veltzer's personal site"
template = "lang_choice.html"
+++

<!--
The root section for the default language, which is the empty "cs" -- see the
note at the top of config.toml for why the default is a language with no
content.

Zola insists the default language has a root _index.md even when that language
has no pages. Neither real language owns "/", so this section renders the
language chooser there (templates/lang_choice.html). Rendering it also puts
"/" in zola's sitemap, which used to be patched in by hand after the build.
-->
