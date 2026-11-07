#!/bin/bash -eu

# Compile the data collection app's Tailwind stylesheet:
#   config/tailwind.collection.config.js + config/tailwind.collection.css
#   -> static/vendor/tailwind-collection.css
#
# Tailwind scans the files the config's `content` lists for class names and
# writes only the utilities they use. The output is committed, like the
# other files in static/vendor/, so the build needs no node. Run this by hand
# after adding a Tailwind class to the data collection app or a plugin; a class it has
# not seen has no rule and does nothing.
#
# Tailwind 3: the configuration format (module.exports with `important` and
# corePlugins) is version 3's; version 4 configures in CSS instead.

cd "$(dirname "$0")/.."
npx --yes tailwindcss@3 \
	--config config/tailwind.collection.config.js \
	--input config/tailwind.collection.css \
	--output static/vendor/tailwind-collection.css \
	--minify
