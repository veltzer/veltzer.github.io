#!/bin/bash -eu

rm -rf docs
mkdir docs
touch docs/.nojekyll
mkdocs build
pydmt build

# copy yaml files from the [data] repo to the right place in this one
mkdir docs/data
cp -f "../data/yaml/"{museums.yaml,video_features.yaml,audio_courses.yaml,video_series.yaml,audible.yaml} "docs/data"
cp -f "../data/raw/topics/games/chess/games.pgn" "docs/data"
