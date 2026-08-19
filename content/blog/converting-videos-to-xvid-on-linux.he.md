+++
title = "המרת סרטונים ל־xvid בלינוקס"
date = 2010-06-11

[taxonomies]
tags = ["לינוקס", "וידאו"]
+++

רציתי להמיר כמה קובצי וידאו במערכת הלינוקס שלי לקודק xvid כדי שאוכל לצפות בהם ב־PS3. הפתרון
שמצאתי היה שימוש בחבילת mencoder.

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
