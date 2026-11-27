+++
date = 2026-11-25
description = "Language is murky because reality is murky. Symbolic AI fought the fuzziness and failed; neural nets embraced it and learned to speak. Complex fields should do the same."
slug = "neural-nets-social-sciences"
title = "What Neural Nets Can Teach Social Sciences"

[taxonomies]
tags = ["science", "epistemology", "philosophy", "law", "economics", "psychology"]
+++

Lawyers spend their careers fighting over words. Where exactly is the line between murder and manslaughter? Between manslaughter and an accident? Every legal system has tried to pin these words down, and every legal system is still arguing about them.

Social scientists will tell you the same story about their own field. Words are murky. Definitions never quite fit. Ask ten sociologists to define "class" or ten psychologists to define "intelligence" and you will get ten answers.

The usual reaction is to treat this as a defect, something to be fixed with sharper definitions. I think that is backwards. **Language is murky because reality is murky.** And the strongest evidence for that comes from an unexpected place: the history of artificial intelligence.

## Two kinds of AI

For decades, AI research bet on logic. Symbolic AI represented knowledge as rules and crisp definitions: a cat is a mammal, a mammal is an animal, if X then Y. Expert systems encoded thousands of such rules by hand. They worked in narrow domains and fell apart the moment the world stepped outside the rulebook. No one ever managed to write down the rules of ordinary language.

Neural nets took the opposite road. A neural net is never told what "cat" means. It sees millions of examples and learns where "cat" sits relative to everything else. [Word embeddings](@/blog/2026-09-11-embeddings-and-arbitrary-signs.md) turn each word into a point in a space of hundreds of dimensions, and meaning becomes a matter of distance and direction. "Cat" is near "dog" and "kitten", far from "theorem", and the boundaries between regions are soft.

The second approach won, decisively. Today's language models are built on it. They succeeded not in spite of being fuzzy but because of it. **They are murky by design, and that is exactly what lets them handle language.**

## The principle: complexity decides

This does not mean logic is useless. Precise equations work wonderfully where the world is precise. Physics deals with a few kinds of parts that behave the same way every time, and Maxwell's equations describe them exactly.

The line is not between "hard" and "soft" sciences. It is between simple and complex systems. Biology already shows this: there is no agreed definition of "species". Lions and tigers can interbreed, and bacteria trade genes freely, so biologists work with several overlapping species concepts. Minds and societies are more complex still: billions of interacting parts, none of them repeating exactly.

In a complex system, any exact rule needs an exception, and the exception needs another exception. If you insisted on laws, you would need billions of them. Language evolved to describe this world, so it inherited the same fuzziness. **Exact tools for simple systems, fuzzy tools for complex ones.** That is why we need neural nets for language: language is complex.

So the general principle is this: **in complex domains, accept and embrace the fuzziness.** Define things by representative examples and reliable statistics, not by ever-sharper definitions. Everything else in this post is that one idea applied.

## The principle in practice

A few examples make the principle concrete. Each is the same idea, seen from a different field.

### Law

Refining legal definitions is a losing game, because every new definition creates new edge cases. Common law already works the other way. Judges reason from precedent, placing a new case near the past cases it resembles, much as a neural net places a new input near its training examples. "Negligence" is not a formula. It is the cloud of all the cases judged negligent.

### Economics

Economics borrowed the tools of physics, precise equations, equilibrium and rational agents, for a system as complex as any. The mainstream models missed 2008. Pattern-based models might predict better. Maybe not: there may not be enough data, and economies rarely repeat under the same conditions. But the clean equations have not earned the benefit of the doubt.

### Politics

The UN has been negotiating a comprehensive convention on terrorism since the 1990s and still has no agreed definition. The fight over the label is a proxy fight. What matters is who is doing what to whom, and judging concrete acts case by case settles more than any definition would.

### Psychiatry

The DSM sorts patients into yes-or-no categories, but real symptoms come in degrees. The field is drifting toward the principle on its own. In 2013 the DSM-5 merged several diagnoses into a single autism spectrum, and newer frameworks such as HiTOP score symptoms on continuous dimensions.

## The catch: representative examples

Defining things by examples has a weakness, and neural nets show it clearly. A model trained on skewed data learns a skewed concept. A public debate fed with cherry-picked anecdotes does the same thing.

So the examples must be representative, or else we work with reliable statistics. This is the same rule for law, for politics and for everything else. The fight does not disappear. It moves from "what is the right definition?" to "which cases count, and are they a fair sample?" That is a better question, because it can actually be answered with evidence.

## Embrace the fuzziness

The lesson neural nets teach the social sciences is simple. The murkiness of language is not a bug to be engineered away. It is an accurate reflection of a complex world.

Stop refining definitions in the hope that the next one will finally be exact. In complex domains, define things by good, representative examples and by reliable statistics. Use equations where the world is simple, and accept fuzziness where it is not.

AI did not invent this truth. Lawyers, psychiatrists and anyone who has argued about politics felt it all along. What AI did was run the experiment: the systems that fought the fuzziness failed, and the systems that embraced it learned to speak.
