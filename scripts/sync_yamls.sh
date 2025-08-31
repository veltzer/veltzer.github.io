#!/bin/bash -eu

files_to_sync=(
    "../data/yaml/museums.yaml:docs/data/"
    "../data/yaml/video_features.yaml:docs/data/"
    "../data/yaml/audio_courses.yaml:docs/data/"
    "../data/yaml/video_series.yaml:docs/data/"
    "../data/yaml/audible.yaml:docs/data/"
    "../data/raw/topics/games/chess/games.pgn:docs/data/"
)

for file_pair in "${files_to_sync[@]}"; do
    src="${file_pair%:*}"
    dest="${file_pair#*:}"
    filename=$(basename "$src")
    
    # Check if file would be updated
    if rsync -av --dry-run "$src" "$dest" | grep -q "$filename"; then
        echo "CHANGED: $filename"
        rsync -av "$src" "$dest" > /dev/null
    else
        echo "unchanged: $filename"
    fi
done
