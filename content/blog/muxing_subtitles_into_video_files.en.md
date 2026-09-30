+++
title = "Muxing Subtitles Into Video Files on Linux"
date = 2013-03-17

[taxonomies]
tags = ["linux", "video", "command-line"]
+++

You have downloaded a film and a matching `.srt` subtitle file, and you would like the two to travel together so that any player shows the subtitles without being told where to find them. There are two ways to do it, and the difference between them matters.

## Soft Subtitles: Keep Them as a Track

A soft subtitle is a separate track inside the container, alongside the video and audio. The player can turn it on or off, and the video is not touched, so there is no quality loss and the operation takes a second because nothing is re-encoded.

With `mkvmerge` from the mkvtoolnix package, into a Matroska file:

```bash
mkvmerge -o movie.mkv movie.mp4 --language 0:eng subtitles.srt
```

With `ffmpeg`, copying every stream and adding the subtitle track:

```bash
ffmpeg -i movie.mp4 -i subtitles.srt -c copy -c:s mov_text movie_out.mp4
```

The `-c copy` is the important part: it says copy the streams as they are rather than re-encode. For an MKV output you can drop the `mov_text` and let the SRT stay an SRT; `mov_text` is the subtitle codec MP4 wants.

Soft is the right default. It is lossless, reversible, and lets the viewer choose.

## Hard Subtitles: Burn Them In

Sometimes you need the subtitles painted into the picture itself, because the target device cannot display a subtitle track, or because you are uploading somewhere that ignores them. This is called burning in, and it does re-encode the video, so it is slower and costs a little quality:

```bash
ffmpeg -i movie.mp4 -vf subtitles=subtitles.srt movie_hardsubbed.mp4
```

Once burned in they cannot be turned off. Only do this when you have to.

## Pairing Files in Bulk

If you have a folder of videos and a folder of subtitles named the same way apart from the extension, you do not want to type the command once per file. Here is a small Python script that pairs them by basename and muxes each one:

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

for video in Path(".").glob("*.mp4"):
    srt = video.with_suffix(".srt")
    if not srt.exists():
        print(f"no subtitle for {video.name}, skipping")
        continue
    out = video.with_name(video.stem + ".subbed.mkv")
    subprocess.run(
        ["mkvmerge", "-o", str(out), str(video),
         "--language", "0:eng", str(srt)],
        check=True,
    )
    print(f"{video.name} + {srt.name} -> {out.name}")
```

It glob-matches every `.mp4`, looks for the `.srt` of the same stem, skips the ones with no match instead of failing, and writes a new `.subbed.mkv` so the originals are left alone. Change the glob and the language tag to suit.

## Which to Use

Reach for soft subtitles unless something forces your hand. They cost nothing, they are undoable, and they leave the choice to whoever is watching. Burn in only for a device or a service that cannot read a subtitle track, and keep the soft-subbed copy as your master.
