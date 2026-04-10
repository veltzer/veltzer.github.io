#!/bin/bash -eu

# Validate source directories exist
if [ ! -d "../data/yaml" ]; then
    echo "ERROR: ../data/yaml directory not found. Clone the data repo first." >&2
    exit 1
fi

# copy data files from the [data] repo to the right place in this one
for f in podcasts.yaml museums.yaml video_features.yaml audio_courses.yaml video_series.yaml audible.yaml; do
    if [ ! -f "../data/yaml/${f}" ]; then
        echo "ERROR: Missing source file ../data/yaml/${f}" >&2
        exit 1
    fi
done
cp -f "../data/yaml/"{podcasts.yaml,museums.yaml,video_features.yaml,audio_courses.yaml,video_series.yaml} "blog/data"

# import audible with type fixes and field cleanup
scripts/import_audible.py "../data/yaml/audible.yaml" "blog/data/audible.yaml"

if [ ! -f "../data/raw/topics/games/chess/games.pgn" ]; then
    echo "ERROR: Missing source file ../data/raw/topics/games/chess/games.pgn" >&2
    exit 1
fi
cp -f "../data/raw/topics/games/chess/games.pgn" "blog/data"

# convert youtube CSV to yaml
scripts/csv_to_yaml.py "../data/raw/topics/video/youtube/all.list.csv" "blog/data/youtube.yaml"

# gzip all data files
for f in blog/data/*.yaml blog/data/*.pgn; do
	gzip -nf "${f}"
done
