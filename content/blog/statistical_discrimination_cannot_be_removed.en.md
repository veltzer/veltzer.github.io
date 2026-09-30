+++
title = "If Groups Differ, a Predictor Will Discriminate, and Blinding It Makes It Worse"
date = 2025-05-05

[taxonomies]
tags = ["politics", "statistics", "ethics"]
+++

Some years ago I wrote a short paper, in Hebrew, about discrimination between black and white Americans by software. The argument was unpopular then and I expect it is unpopular now, so let me state it as carefully as I can, because the careful version is the only one worth defending.

**If two groups differ statistically in some characteristic that matters to a decision, then any predictor that is any good will treat members of the two groups differently, and a predictor forbidden from doing so will be worse at its job.** This is not a claim about software ethics. It is arithmetic, and the arithmetic does not care what we think of it.

## The Setup

Take any decision that is made by prediction: who gets a loan, who gets bail, who gets flagged at the airport, whose CV gets read. The decision-maker wants to estimate something about an individual, repayment, reoffending, threat, competence, and has only partial information.

Now suppose two groups differ in the base rate of the thing being predicted. It does not matter why. It could be history, it could be poverty, it could be a hundred things that are nobody's fault. The difference exists in the data.

A predictor that knows the group will use it, because it is information, and information improves prediction. That is what a predictor is for. It will therefore produce different outcomes for the two groups, on average, and someone will call that discrimination, and they will be right to, in the plain sense of the word.

## The Blinding Move

The standard remedy is to remove the group variable. Do not tell the model the race, the sex, the postcode.

This fails twice.

It fails first because the group is encoded in everything else. Name, address, school, employment history, the shops you use: each carries a fraction of the signal, and a decent model reconstructs the group from the fragments without ever being told. You have not removed the information; you have hidden it from yourself while the model still has it.

It fails second, and more fundamentally, even if the blinding were perfect. A predictor that cannot use a real difference makes more mistakes. And the mistakes do not fall evenly. When you force a single threshold onto two populations with different base rates, one group gets more false positives and the other more false negatives than they would under a predictor that knew. **The blind predictor is not fair. It is unfair in a different pattern, and less accurate on top.**

You cannot make the difference in the data disappear by refusing to look at it. You can only choose which errors you would rather make.

## The Confusion That Makes This Hard to Discuss

Most of the heat in this debate comes from running two questions together.

The first is a question about groups: do they differ, and does a predictor that knows it perform differently on them? That question has an answer in the data, and the answer is frequently yes.

The second is a question about individuals: what should happen to a particular person who belongs to a group with an unfavourable statistic? That question is not answered by the data at all. A base rate tells you about a population. It tells you almost nothing about the person in front of you, who may be anywhere in the distribution.

I have written about how [a label is only useful because it carries information](@/blog/labels_carry_information.en.md). The flip side is that the information a label carries is statistical, and treating a statistical fact as a fact about an individual is the actual error. **The predictor is not wrong to notice the difference. The decision-maker is wrong to stop noticing there.**

## Where the Real Choice Lives

So the honest question is not whether to allow the difference into the model. It is already there and will not leave. The honest question is what a society wants to do with predictions about individuals that are shaped by facts about groups.

That is a political question and it has several defensible answers.

One is to accept the prediction and its uneven outcomes, on the grounds that accuracy saves the most people overall. Bail decided by the best available predictor keeps more dangerous people in and lets more harmless people out than any alternative, and the alternative is a judge's gut, which is also a predictor and a worse one.

Another is to decide that certain decisions should not be made by prediction at all, whatever the cost in accuracy, because the harm of being judged by your group is a harm we will not impose in that domain. That is a coherent position. It has a price, and the price should be stated: more bad loans, more wrong releases, more missed threats, or whichever error the domain produces.

A third is to use the prediction and then correct the distribution of errors deliberately, at the decision stage rather than inside the model, so that the trade-off is visible and voted on rather than hidden in a threshold.

What is not defensible is the position that dominates the public conversation: that a fair predictor exists, that it would show no group difference, and that anyone whose model shows one has built it wrong. **There is no such predictor. Demanding it produces either a lie about the model or a worse model, and usually both.**

## Why This Matters Beyond Software

Software made the problem visible because software has to write the rule down. A loan officer who discriminated had a feeling; a scoring model has a coefficient, and the coefficient can be read. The result is that we are now arguing about a thing humans have always done, in the first setting where it can actually be measured.

That is an opportunity. For the first time we can see the trade-off exactly: this much accuracy for this much uneven outcome, in this domain, at this threshold. We could decide it openly. Instead the conversation insists the trade-off is an artefact of bad engineering, and demands that engineers make it go away.

They cannot. Nobody can. The difference is in the world, the predictor reports it, and the only question left is ours: what we do to the person in front of us, knowing what the statistic says and knowing what it cannot say. That is a question for a society to answer, and it would be a good deal easier to answer if we stopped pretending it was a bug.
