+++
title = "Converting videos to xvid on Linux"
description = "A bash script that uses mencoder to convert videos to the xvid codec in place, so they play on a PS3, stopping at the first file that fails."
date = 2010-06-11

[taxonomies]
tags = ["linux", "video"]
+++

I wanted to convert some video files on my Linux system to the xvid codec so that I could see them on my PS3. The solution I found was using the mencoder package.

```bash
#!/bin/bash

# this script converts videos given to it to the xvid codec, IN PLACE,
# this means it replaces the original files...

for x in "$@"; do
    echo "$x"
    y="$x.tmp"
    mencoder "$x" -ovc xvid -oac copy -xvidencopts fixed_quant=4 -o "$y"
    ret=$?
    if [[ $ret -eq 0 ]]; then
        mv "$y" "$x"
        ret=$?
        if [[ $ret -ne 0 ]]; then
            echo "problem moving file $x"
            break
        fi
    else
        echo "problem converting file $x"
        break
    fi
done
```
