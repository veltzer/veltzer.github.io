+++
title = "Why Elections Come Out Fifty-Fifty Even When Every Issue Has a Clear Majority"
date = 2026-08-06

[taxonomies]
tags = ["politics", "statistics", "probability"]
+++

Elections in mature democracies have a habit of landing near fifty-fifty. People explain this with stories about polarisation, about the media, about parties chasing the median voter. I think there is a simpler and more mechanical explanation, and it needs no psychology at all. It falls out of arithmetic the moment you bundle issues into parties.

## The Model

Take a population and six issues. On every issue the public is not divided at all: seventy percent hold one view and thirty percent the other. Every single question has a clear majority.

Now form two parties. Party A takes the majority position on three of the issues and the minority position on the other three. Party B does the reverse. Each voter looks at the six issues, counts how many times A agrees with them and how many times B does, and votes for whichever agrees more. Ties abstain.

What happens?

## The Script

I wrote this down years ago as a small simulation, because I did not trust the intuition either way.

```python
#!/usr/bin/env python3
import random

issues_a = 3          # issues on which party A holds the majority view
issues_b = 3          # issues on which party B holds the majority view
majority = 0.7        # share of the public on the majority side of each issue
population = 100_000_000

for_a = for_b = 0
for _ in range(population):
    side = 0
    for _ in range(issues_a):
        side += 1 if random.random() < majority else -1
    for _ in range(issues_b):
        side -= 1 if random.random() < majority else -1
    if side > 0:
        for_a += 1
    elif side < 0:
        for_b += 1

print(f"for_a {for_a}")
print(f"for_b {for_b}")
```

Running it with a smaller population, two hundred thousand voters, gives roughly sixty-five thousand for A, sixty-five thousand for B, and seventy thousand tied. Split the ties any way you like; the vote is fifty-fifty to within noise. Raise the majority on each issue from seventy to ninety percent and the result does not budge; only the number of ties grows.

## Why

The result is forced by symmetry. Party A wins a voter on each of its three majority issues with probability 0.7 and loses that voter on each of B's three majority issues with the same probability. The two halves of the ledger are mirror images. Whatever distribution of scores A produces, B produces the reverse, and the expected vote is exactly even.

**The majority on every issue is real, and it cancels out completely once the issues are bundled.** Nothing about the public changed. Seventy percent of people still want each thing. But they want the six things in different combinations, and a two-party system forces every combination through one binary choice, where the combinations sum to zero.

If the bundles are unequal the symmetry breaks. Give A three majority issues and B only two, and A wins something like fifty-eight to forty-two. So the fifty-fifty outcome is not a law of nature; it is what you get when two parties have divided the popular positions between them roughly evenly. And parties will do exactly that, because a party holding all the majority positions would simply win, and its opponent would adjust until it did not.

## What It Explains

It explains why elections feel like coin tosses decided by the last week: when the structural expectation is even, the outcome is whatever noise was present on the day.

It explains why the loser of every election is convinced the country has gone mad, when the country has not moved at all. Half the voters lost on three issues they cared about and won on three they cared about less.

And it explains why [an election extracts almost no information](@/blog/fifty_fifty_elections_extract_no_information.en.md) about what the public wants. The information was there, seventy percent on every question, and the bundling destroyed it before it reached the ballot.

The model is a toy. Real issues are correlated, real voters weight them unequally, real parties are more than two lists of positions. But the mechanism it isolates is present in every real election, and it is worth seeing in its pure form: **a system that asks one question about six things cannot hear the answer to any of them.** Ask the six questions separately and you get six majorities. Ask them as a package and you get a coin.
