---
tags:
  - linux
  - video
  - multimedia
date: 2010-06-11
---

# Converting videos to xvid on Linux

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
