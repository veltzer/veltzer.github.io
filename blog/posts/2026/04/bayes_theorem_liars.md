---
tags:
  - probability
  - statistics
  - bayes
date: 2026-04-04
---

# Why Known Liars Making a Claim Actually Reduces Its Probability: A Bayesian Explanation

## The Intuition

Most people think that if someone makes a claim, it should at least slightly increase
our belief that the claim is true - after all, why would they say it if it weren't true?
But Bayes' theorem shows us something counterintuitive: if the person making the claim
is a known liar, their assertion can actually make the claim *less* likely to be true
than it was before they opened their mouth.

## A Quick Refresher on Bayes' Theorem

Bayes' theorem tells us how to update our beliefs when we receive new evidence:

**P(A|B) = P(B|A) * P(A) / P(B)**

Where:

- **P(A|B)** is the probability of A being true, given that we observed B
- **P(B|A)** is the probability of observing B if A were true
- **P(A)** is our prior probability of A being true
- **P(B)** is the overall probability of observing B

## Setting Up the Problem

Let's say there's a claim C, and a known liar L asserts that C is true.

We need to figure out:

- **P(C)** - our prior belief that C is true before the liar speaks. Let's say 50% (we have no idea).
- **P(L says C | C is true)** - the probability the liar would assert C if C were actually true.
- **P(L says C | C is false)** - the probability the liar would assert C if C were actually false.

Here's the key insight: a known liar is someone who is *more likely* to say things that
are false than things that are true. So:

- **P(L says C | C is true)** = 0.2 (a liar rarely tells the truth)
- **P(L says C | C is false)** = 0.8 (a liar usually lies)

## Running the Numbers

We want **P(C is true | L says C)**.

First, compute P(L says C):

```
P(L says C) = P(L says C | C is true) * P(C) + P(L says C | C is false) * P(not C)
            = 0.2 * 0.5 + 0.8 * 0.5
            = 0.1 + 0.4
            = 0.5
```

Now apply Bayes' theorem:

```
P(C is true | L says C) = P(L says C | C is true) * P(C) / P(L says C)
                         = 0.2 * 0.5 / 0.5
                         = 0.2
```

We started with a 50% belief that C was true. After the known liar asserted C,
our belief **dropped to 20%**. The liar's endorsement is actually evidence *against*
the claim.

## Why This Matters

This result has profound real-world implications:

### Propaganda and Disinformation

When a source with an established track record of lying makes a claim, rational observers
should treat that claim with *more* skepticism than they had before, not less. The claim
is tainted by its source. This is not an ad hominem fallacy - it is correct probabilistic
reasoning.

### The Inverse is Equally Useful

If a known liar *denies* something, that denial is actually evidence *for* the thing
being true. If an authoritarian regime denies committing atrocities, and that regime
has a strong track record of lying, the denial should increase your belief that the
atrocities occurred.

### Stacking Liars Does Not Help

If multiple known liars independently assert the same claim, each additional liar's
assertion *further reduces* the probability. Ten liars all saying the same thing
is not reinforcement - it is ten pieces of evidence pointing *away from* the claim.
This assumes their assertions are independent; if they're coordinating, it's
essentially one assertion from one source.

### Religious Texts and Religious Claims

This reasoning applies directly to religious texts and claims made by religious figures.
Religious texts such as the Bible, the Quran, and others contain numerous claims that
have been demonstrably shown to be false: the age of the earth, the global flood,
the creation narrative, the sun standing still, and many more. These texts have,
by any empirical standard, an extremely poor track record of making true claims
about the physical world.

Now consider what happens when these same texts make *unfalsifiable* claims -
the existence of God, an afterlife, a soul, divine purpose, or miracles that
conveniently left no trace. A naive observer might say "well, we can't disprove
those claims." But Bayes' theorem tells us something stronger: the very fact that
a source with such a poor track record is the one making these claims is *evidence
against them*. If the Bible gets geology, biology, cosmology, and history wrong
repeatedly, its assertions about metaphysics deserve *less* credence, not a free pass
simply because they are unfalsifiable.

The same applies to religious authorities. A priest, rabbi, or imam who makes
verifiably false claims - about history, science, or even the contents of their
own texts - establishes themselves as an unreliable source. When that same person
then asserts the existence of God or the truth of their theology, Bayes' theorem
tells us their assertion should *lower* our posterior probability, not raise it.
The more such unreliable sources pile on to the same claim, the worse it gets -
as we saw with stacking liars above.

This is not a proof that God does not exist. It is a mathematical observation that
the primary sources making the claim have disqualified themselves as evidence *for*
that claim. If your best witnesses are known liars, calling them to the stand hurts
your case.

### Trust is Information-Theoretic

This analysis shows that trust is not just a social nicety - it has rigorous
mathematical consequences. A source's reliability directly determines whether their
statements function as evidence *for* or *against* their claims. A perfectly reliable
source's assertions would push your belief toward 100%. A perfectly unreliable source's
assertions push your belief toward 0%. And a source that is right exactly half the time?
Their statements carry zero information - you can ignore them entirely.

## The Takeaway

Bayes' theorem formalizes what many people intuitively sense but struggle to articulate:
the credibility of a source matters just as much as the content of their claim. Known
liars asserting something is true is, mathematically speaking, evidence that it is false.
The next time someone with a track record of dishonesty makes a bold claim, remember:
their very act of claiming it has made it less likely to be true.
