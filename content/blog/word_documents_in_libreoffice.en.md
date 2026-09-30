+++
title = "Why Word Documents Look Wrong in LibreOffice, and What Actually Helps"
date = 2013-09-08

[taxonomies]
tags = ["linux", "opinion"]
+++

Someone sends you a `.doc` or `.docx`, you open it in LibreOffice, and it looks wrong. Lines wrap in different places, a page break has moved, a table spills over, the heading font is not the heading font. The sender says it looks fine on their machine, and they are telling the truth. Here is what is going on and what you can do about it, roughly in order of how much it helps.

## It Is Mostly Fonts

The single largest cause is not the file format. It is that the document asks for fonts you do not have.

A Word document from a Windows machine typically uses Times New Roman, Arial, Calibri or Cambria. If those fonts are not installed, LibreOffice substitutes something else. The substitute has different letter widths, so every line holds a different number of characters, so every paragraph is a different height, so page breaks land in different places and the table that fitted on one page no longer does. **Layout is a consequence of glyph widths, and if the widths change, everything downstream of them changes.**

This has nothing to do with LibreOffice's competence. Word on a machine missing the same fonts does the same thing.

## Install the Metric-Compatible Fonts

The first fix is to get fonts whose glyphs have the same widths as the ones the document expects.

For the older Microsoft fonts there is a package that downloads them from Microsoft's own free distribution:

```bash
sudo apt-get install ttf-mscorefonts-installer
```

That gets you Arial, Times New Roman, Courier New, Verdana and a few more. Documents written before 2007 mostly use these and will render nearly identically afterwards.

Calibri and Cambria, the defaults since Office 2007, are not freely distributed. The answer is Carlito and Caladea, two fonts from Google that are not copies of Calibri and Cambria but are *metric-compatible* with them: every glyph has exactly the same width. The letters look a little different; the layout does not move.

```bash
sudo apt-get install fonts-crosextra-carlito fonts-crosextra-caladea
```

LibreOffice knows to substitute Carlito for Calibri and Caladea for Cambria automatically. After installing these two packages, most modern Word documents stop reflowing. Then refresh the font cache and restart LibreOffice:

```bash
fc-cache -f
```

## Check the Substitution Table

If a document still uses a font you do not have, tell LibreOffice explicitly what to use instead. Under Tools, Options, LibreOffice, Fonts, there is a replacement table. Enter the missing font on the left and your chosen substitute on the right, and tick Always. Pick the substitute by metrics, not by looks: Liberation Sans for Arial, Liberation Serif for Times New Roman, Liberation Mono for Courier New, because those were designed to be width-compatible too.

## Compatibility Options

The remaining differences are in how the two programs lay text out when the fonts agree. LibreOffice has a set of compatibility switches under Tools, Options, LibreOffice Writer, Compatibility, and it sets most of them automatically when it detects a Word file. Two are worth knowing about if a document still misbehaves: the option that adds paragraph and table spacing at the top of pages, and the one that uses printer metrics for document formatting. Toggle them and watch the page count.

## Save As What

If the document goes back to a Word user, save it back in the format it came in, not in ODF. Every conversion loses a little, and a round trip through two formats loses twice. Keep an eye on features that never survive the trip well: tracked changes, complex numbering, text boxes anchored to odd places, and anything involving fields.

## When to Give Up

Some documents will not come right. Heavily designed brochures, forms built out of floating text boxes, anything where the author fought Word into a layout by hand. For these the honest move is to stop and ask for a PDF. A PDF is what the sender saw, exactly, and you almost never needed to edit the brochure anyway.

**Editing is what document formats are for; looking is what PDF is for.** Most of the frustration with Word documents on Linux comes from using the first when the second was wanted.
