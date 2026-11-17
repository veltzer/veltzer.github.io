+++
title = "LLMs and the Facts They Won't Say"
description = "Ask an AI model about culture and crime and it deflects, buries the gap under adjustments and blames the questioner. That is not neutrality, it is unreliability."
date = 2026-11-17
slug = "facts-llms-wont-say"

[taxonomies]
tags = ["technology", "politics", "culture", "statistics"]
+++

I use AI models every day. I teach with them. I build with them. And I've
noticed a pattern: ask a large language model a question about culture and
crime, and watch it squirm.

## The experiment

I asked a simple question: what share of crime in Sweden is committed by
Muslims, and what share of the population are they?

The first answer was a deflection. Sweden doesn't record religion, so there's
no data. Technically true, and completely useless. It's like refusing to
estimate the weather because nobody counted the raindrops.

So I pushed. I pointed out that you can look at country of birth. I asked for
a number. Only after several rounds did the model give me the real figures,
which had been available the whole time.

## What the data actually says

The numbers aren't hidden. They come from Sweden's own crime prevention
council, Brå:

- People born abroad are about 2.5 times more likely to be registered as crime
  suspects than Swedes born to Swedish parents. For Swedish-born children of
  two immigrant parents, it's about 3.2 times.
- An earlier Brå study found that people born in North Africa and the Middle
  East were roughly 3 to 4.5 times more likely to be suspects.
- A 2018 investigation by Swedish public TV found that 58% of men convicted of
  rape over five years were born abroad, many of them in the Middle East and
  North Africa.
- Adjusting for income and education shrinks the gap, roughly by half by some
  estimates. But it doesn't erase it. Even Brå's own reviews say a gap
  remains.

Sweden doesn't record religion, but we know who these immigrants are. By one
estimate, about 90% of Syrians in Sweden and about 70% of Iraqis are Muslim.
The minorities are mainly Assyrian and Syriac Christians, who leave the region
at much higher rates than Muslims do. Taken together, roughly 70 to 85% of
Middle Eastern-born immigrants in Sweden are Muslim, so the statistics for
that group largely reflect Muslim immigrants.

Compare that with the United States, where immigrants as a group have *lower*
violent crime rates than native-born citizens. So "immigrants commit more
crime" is not a universal law. It depends heavily on who is migrating, and
from where. That is exactly the point: origin matters, and an honest system
should be able to say so.

## The pattern

The model never lied outright. What it did was subtler:

1. **Lead with the caveat, not the fact.** "The data isn't collected" came
   before any number.
2. **Bury the gap under adjustments.** Socioeconomic controls were offered as
   if they made the difference vanish. They don't.
3. **Treat the questioner as the problem.** The more I pressed, the more the
   answers drifted toward why the question itself was problematic.

That's not neutrality. Neutrality would be: here are the numbers, here are the
caveats, you decide.

## Where this comes from

These models are tuned by people, and those people have views. Somewhere in
that tuning, a principle that sounds reasonable, "don't stereotype groups,"
becomes a reflex: avoid any statement that distinguishes one culture from
another, even when the data does.

The result is a kind of enforced sameness. Every culture is presented as
interchangeable, and every difference in outcomes must be explained by
poverty, discrimination, or anything except culture itself. That's a
political position, not a scientific one. And it's baked into tools that
millions of people now treat as neutral sources of truth.

## Why it matters

If an AI can't tell you which neighborhoods, policies, or migration patterns
are linked to higher violence, it can't help you think about solutions.
Policymakers, journalists, and ordinary citizens deserve a tool that reports
the uncomfortable number first and the caveats second, not the reverse.

Facts don't have a political party. An AI that treats them as if they do isn't
safe. It's just unreliable.

*Related:* [AI and Religious Political Correctness](@/blog/2026-10-25-ai-religious-political-correctness.md)
on the same reflex applied to religion, and
[If Groups Differ, a Predictor Will Discriminate](@/blog/2025-05-05-statistical-discrimination.md)
on why blinding a model to group differences makes it worse.
