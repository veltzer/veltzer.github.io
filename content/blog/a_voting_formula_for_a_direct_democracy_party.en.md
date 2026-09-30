+++
title = "A Voting Formula for a Party That Takes Its Orders From the Public"
date = 2023-07-12

[taxonomies]
tags = ["direct-democracy", "israel", "politics"]
+++

Suppose a party runs for the Knesset on one promise: it has no platform of its own, and on every vote it will do what the public tells it to do in an online poll held before the vote. This is the cheapest route to direct democracy that I know of. It needs no constitutional change, no referendum law, no permission from anyone. It only needs a party willing to be a pipe.

The moment you try to build the pipe you hit a technical question that turns out to be interesting: **how should such a party cast its seats?**

## The Two Naive Answers

The first naive answer is proportional. If the public voted 66 percent in favour, then 66 percent of the party's members vote in favour and 34 percent against. This feels honest. It is also useless when the party is small. A party with one seat cannot split itself; a party with three seats that votes two to one has thrown away a third of the only power it has, on every single vote, forever.

The second naive answer is winner-takes-all. If the public is in favour by any majority, the entire party votes in favour. This is what a small party should obviously do: its one seat should go where the public's majority is. But it is wrong when the party is large. A party holding all 120 seats that votes unanimously on a 51 percent public decision has erased the 49 percent completely, which is exactly the kind of flattening the whole exercise was meant to abolish.

So the right rule depends on the party's size. Small parties should behave like a single vote, and a party that has grown to fill the house should behave like the public itself.

## The Formula

Two inputs. Let `v` be the fraction of the public in favour of the proposal, from 0 (nobody) to 1 (everybody). Let `s` be the party's share of the house, from 0 (no seats) to 1 (all 120 seats). Let `round(v)` be the majority verdict: 1 if `v` is at least one half, 0 otherwise.

Then the fraction of the party that votes in favour is:

```text
party_vote = round(v) * (1 - s) + v * s
```

and the number of members who vote in favour is:

```text
n = round(120 * s * party_vote)
```

The formula is a blend. When the party is tiny, `1 - s` is nearly 1 and `s` is nearly 0, so the result is essentially `round(v)`: winner takes all. When the party is the whole house, `1 - s` is 0 and the result is exactly `v`: perfect proportionality. In between, it slides smoothly from one to the other.

## Why It Stays Between 0 and 1

This matters, because a fraction of a party outside that range is nonsense.

The lower bound is easy. Every term (`v`, `round(v)`, `s`, `1 - s`) is non-negative, so the sum is non-negative.

For the upper bound, split on the majority. If `v` is at least one half, then `round(v)` is 1 and `party_vote = (1 - s) + v * s`. Since `v` is at most 1, this is at most `(1 - s) + s`, which is 1. If `v` is below one half, then `round(v)` is 0 and `party_vote = v * s`, and the product of two numbers that are each at most 1 is at most 1.

**So the rule never asks the party to cast more votes than it has.**

## Three Worked Examples

Take a proposal the public supports by two thirds, so `v` is 0.6667.

**One seat.** Then `s` is 1/120, about 0.0083. The formula gives `1 * 0.9917 + 0.6667 * 0.0083`, about 0.997. The party votes unanimously in favour. Winner takes all, as a single seat must.

**Sixty seats.** Then `s` is 0.5. The formula gives `1 * 0.5 + 0.6667 * 0.5`, which is 0.8333. Fifty of the sixty members vote in favour and ten against. More than proportional, less than unanimous: the party is large enough to afford some representation of the minority, but not yet large enough to be the whole electorate.

**All 120 seats.** Then `s` is 1. The formula gives `0 + 0.6667`, so eighty members vote in favour and forty against. The house now reproduces the public exactly, which is what it should do once it *is* the public.

## What the Formula Is Really Saying

Notice what the design encodes. A small pipe should maximise its effect, because a small party's whole reason for existing is to push the public's majority through a door the other parties keep shut. A large pipe should maximise its fidelity, because a large party's whole reason for existing is to be the public in the room.

The transition between the two goals is not a matter of principle; it is a matter of arithmetic, and arithmetic is what settles it here. That is the general lesson I take from the exercise. **Most of the objections to direct democracy are objections to an implementation that nobody has bothered to design.** Design one and the objections turn into parameters.

There is nothing Israeli about the formula except the number 120. Replace it with the size of any legislature and the rest goes through unchanged.
