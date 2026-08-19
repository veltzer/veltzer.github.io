+++
title = "Understanding Is Compression"
date = 2011-07-05

[taxonomies]
tags = ["epistemology", "science", "theory"]
+++

Here is a definition I think is exactly right, and which turns a vague notion into a measurable one: **knowledge is compression of information. Understanding something means being able to say it shorter.**

This is not a metaphor. It gives you a number.

## The Sequence

Given 1, 4, 9, what comes next?

You say 16. But −7 is also defensible: there is a polynomial that produces 1, 4, 9, −7, and it is a perfectly legitimate function. Infinitely many functions pass through any finite set of points.

So why is 16 better? **Because its formula is shorter.** *n²* against a fourth-degree polynomial with awkward coefficients. Nothing else distinguishes them — not evidence, since both fit the data exactly. The whole of the preference is compression.

## Ptolemy, Newton, Einstein

The same criterion sorts the history of astronomy, and does it more cleanly than any story about evidence.

Ptolemy's system worked. It predicted planetary positions with real accuracy, and it did so with epicycles — circles on circles, tuned individually. But he had no account of *why* Mars needed its particular epicycle and Neptune another. Each was a separate stipulation, fitted to that planet.

Newton explained everything Ptolemy explained, using laws that fit on an index card, with no per-planet adjustments.

Picture a line running from **describing** phenomena to **understanding** them. Recording planetary positions in a table is pure description — maximal length, zero compression. Newton's laws sit at the far end: enormous coverage from almost nothing. Ptolemy sits in the middle. He saw there were cycles, which is real compression, but paid for the exceptions individually.

**The test case.** Newton did not in fact predict every orbit correctly — Mercury's perihelion precession was wrong. So consider "Newton Plus": Newton's laws with a special exception patched in for Mercury.

Newton Plus explains *everything*. Is it a better theory?

No — and now you can say precisely why. It covers more but compresses worse: writing it down takes the laws plus the exception. **This is what special pleading costs you, quantified.** Einstein then beat Newton the same way Newton beat Ptolemy: simpler laws, everything Newton explained, plus Mercury, plus predictions nobody had asked for.

## Why This Is Not Just Occam's Razor

Occam says the simplest explanation tends to be correct, all else equal. That is a heuristic and it is famously vague — simplest in what respect? measured how?

Compression gives you the missing piece. You can ask **how much data a theory covers and how many bits it takes to state**, and compare two theories on that ratio. "Simpler" stops being an aesthetic judgement and becomes an arithmetic one.

It also explains *why* Occam works, which Occam does not. A theory that compresses well has found real structure in the data, because that is what compression is. A theory that compresses badly is storing the data rather than explaining it.

## The Corroboration From Machine Learning

An autoencoder takes input, squeezes it through a narrow layer, and reconstructs it. The narrow layer forces it to discard everything not needed for reconstruction — which means it must find what the data actually consists of.

Human language is enormously redundant: connectives, agreement markers, syllables carrying no information. What an autoencoder trained on sentences must find is the meaning, because meaning is exactly what survives maximal compression.

Which is why machine translation works the way it does: encode the sentence to a compressed representation, then decode into the other language. **The compressed representation is the meaning.** Nobody designed it that way for philosophical reasons; it is what worked.

That two entirely separate lines — the philosophy of scientific explanation and the engineering of neural networks — arrive at the same identification seems to me the strongest evidence that the identification is right.

Understanding is compression.
