#!/bin/bash -eu

# copy yaml files from the [data] repo to the right place in this one
cp -f "../data/yaml/"{museums.yaml,video_features.yaml,audio_courses.yaml,video_series.yaml,audible.yaml} "docs/data"
