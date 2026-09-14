+++
title = "Philosophy and the Scientific Revolution: The Failure of Ambiguity"
date = 2026-09-14

[taxonomies]
tags = ["philosophy", "science", "epistemology", "history"]
+++

The usual story about the Scientific Revolution is that people started looking at the world instead of reading Aristotle about it. That is part of it, but observation alone does not explain the break. Medieval scholars observed plenty. Astrologers kept meticulous tables, physicians watched patients for a lifetime, and alchemists ran more experiments than most modern chemistry undergraduates. What changed in the seventeenth century was not the amount of looking. It was a decision about what you are allowed to build a theory out of.

The decision was this: start from a small number of primitives that mean exactly one thing, and construct everything else from them. Philosophy never made that decision, and that is why it is where it is.

## What Newton Refused to Do

Before Newton, the explanation of why things fall was that heavy bodies have a natural tendency toward the centre. The explanation of why opium puts you to sleep, in Molière's famous parody, was that it has a dormitive virtue. Fire rises because its nature is to rise. These explanations were satisfying, and they were worthless, and the two facts are related. A word like "tendency" or "virtue" or "nature" can be attached to any phenomenon after the fact, so it explains everything and predicts nothing.

Newton did not write a treatise on the nature of motion. He picked a handful of bare terms, point mass, distance, time interval, force as a vector, and he gave each one a definition tight enough that two people using it could not disagree about what it referred to. Then he invented the calculus needed to say how those terms relate, and he derived the orbits of the planets from three laws that fit on one page. The primitives were poor in meaning, deliberately so. All the richness came out of the construction.

Chemistry did the same thing a century later, and it could only do it by throwing words away. Phlogiston was a real theory held by serious people. It had a name, a literature and a set of qualitative principles, and none of that saved it once weight could be measured to the milligram. The field became a science at the moment it agreed that its primitives would be discrete elements with fixed masses and nothing else.

The twentieth century repeated the move in the most abstract territory imaginable. Shannon founded information theory by refusing to say anything about meaning at all. Information was the reduction of uncertainty, the unit was the bit, and the question of what a message was about was ruled out of scope. Turing did the same for computation: an abstract machine with a tape, a head and a finite table of state transitions, and every algorithm anyone would ever write turned out to be expressible in it. Both men were asked, in effect, to define something deeply human, and both answered by defining something almost insultingly simple and then showing it was enough.

The pattern is the same every time. Take the complex phenomenon, decompose it into primitives that are simple, unambiguous and checkable, and rebuild the complexity from them. The direction is always bottom up.

## Philosophy Went the Other Way

Metaphysics, epistemology and most of what gets called continental philosophy did not adopt this discipline, and they did not adopt it for a specific reason: they took natural-language words as their starting point. Mind, free will, substance, knowledge, justice, goodness, being. These are the primitives of philosophy, and not one of them is primitive.

Natural language evolved to coordinate a band of primates. It is a noisy heuristic for getting other people to do things, and its words are compressed bundles of use cases that happened to travel together. "Knowledge" covers knowing a fact, knowing how to ride a bicycle, knowing a person and knowing that something feels wrong, and there is no reason to believe those share an underlying structure just because English gave them one verb. To treat the word as a unit of reality is to assume that the accidents of a language's history carve the world at its joints.

Three things go wrong when a discipline builds on such words.

The first is reification. Because there is a noun, there must be a thing. Because people say "consciousness", there must be a single coherent entity that either is or is not present in a system, and the debate becomes about where it is rather than about whether the noun names one thing at all.

The second is circularity. When your terms are fuzzy, the only move available is to propose a definition, and the only counter-move is to propose another one. Two and a half millennia of argument about what justice is have this shape. It looks like inquiry, but no mechanism is ever uncovered, because the argument is over which words to prefer, and preferences do not converge.

The third is mistaking confusion for depth. When ambiguous terms produce a paradox, which they reliably do, the philosopher announces a profound mystery of the universe. Zeno's arrows, the ship of Theseus, the problem of the heap. In every case the "mystery" evaporates the moment someone supplies a primitive precise enough to compute with, and in every case the philosophical literature had treated the vagueness of the original words as a feature of the world rather than of the words.

Wittgenstein saw much of this. Philosophical problems arise, he said, when language goes on holiday, when words are lifted out of the practices that gave them a use and treated as metaphysical absolutes. That is a correct diagnosis. But the linguistic turn stopped at the diagnosis. Having noticed that the words were the problem, philosophy did not do the scientific thing and replace them with better tools. It kept the words and declared the disease incurable. I have written about [that specific surrender](@/blog/wittgenstein_alchemy_of_meaning.en.md) elsewhere.

## Every Success Left the Building

There is a clean historical test of this argument. Look at what happened to the parts of philosophy that did adopt bottom-up construction.

Natural philosophy became physics as soon as it swapped qualitative discourse about natures and tendencies for measurable quantities and laws. Nobody now calls Newton a philosopher, although his book has the word in its title. The philosophy of the organism, the long argument about what distinguishes living matter, became molecular biology as soon as heredity was located in a discrete chemical structure rather than a vital principle. The vitalists were not defeated in debate. They were made irrelevant by a molecule. Logic, to the extent it became formal, moved into mathematics and computer science, and the parts that stayed behind are the parts that resisted formalisation.

What remains in the philosophy department, then, is not a random sample of hard questions. It is a selected sample: the residue of questions that refused to be rebuilt from primitives, or were protected from it. This is worth stating plainly, because it inverts the usual self-image. Philosophy did not keep the deepest problems. It kept the ones whose vocabulary was never fixed, and it kept them precisely by never fixing the vocabulary. The ambiguity is not an obstacle the discipline has been fighting. It is the mechanism by which the discipline's problems have been preserved.

## The Case of Meaning Itself

The clearest demonstration is the one closest to home for philosophy, which is the theory of meaning.

Philosophers have argued about what a concept is for as long as there have been philosophers. Plato put meanings in a realm of forms. Frege and Russell dissected sense and reference. The ordinary-language school catalogued how words are actually used. The literature is enormous and it is very hard to name one thing it settled.

Then, over about a decade, computer scientists built a working theory of meaning, and they did it by ignoring the entire debate. They did not ask what a word's essence is. They asked which words occur near it, counted, and mapped each word to a point in a space of a few hundred or a few thousand dimensions such that words with similar contexts land near each other. The primitives were vectors, dot products and a probability distribution over a corpus. Nothing in the construction refers to meaning at all.

And meaning fell out. Similarity became distance. Categories became regions with graded membership, exactly the fuzzy family-resemblance structure philosophers had said was unformalisable. Analogy became subtraction: king minus man plus woman lands next to queen, and nobody put it there. I have written about [why those vectors need so many dimensions](@/blog/word_embeddings_arbitrariness_of_the_sign.en.md) and I will not repeat it, but the point for this argument is the method. Meaning became measurable the moment somebody agreed to build it from primitives that were not themselves words.

This is the pattern from the first section, replayed on the subject philosophy considered most its own. The result was not a contribution to the philosophical debate. It was the end of the debate's relevance, in the way that chemistry was the end of alchemy's relevance, and for the same reason.

## What Would Have to Change

The lesson of the Scientific Revolution is not that observation beats speculation. It is that understanding is built from the bottom up, and that the bottom has to be made of things that mean one thing each. Inherited words do not qualify. They are what a theory has to explain, not what it is allowed to explain with.

I have argued before that [philosophy as practised fails because it never fixes its terms](@/blog/why_philosophy_fails.en.md). This post is the historical case for the same conclusion. For philosophy to become something other than a permanent scholastic backwater, it would have to do three things that the sciences did centuries ago. Stop treating vernacular nouns as windows onto ontology. Break every loaded concept down into primitives precise enough that a disagreement about them can be settled. Prefer a formal model that can be wrong to a dialectic that cannot.

I do not expect this to happen, because a philosophy that did it would stop being called philosophy. That has been the fate of every branch that tried. But it is worth being clear about why the questions that remain have remained. They are not too deep for the method. They have simply never been submitted to it.
