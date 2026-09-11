+++
title = "Wittgenstein Is to Word Embeddings What Alchemy Is to Chemistry"
date = 2026-09-10

[taxonomies]
tags = ["philosophy", "programming", "epistemology", "science"]
+++

Astrology was not stupid. The people who practised it noticed that the sky moves in cycles, that the cycles are regular, and that some of them line up with the seasons, the tides and the harvest. Those are real observations, and they are the observations astronomy was built on. Alchemy was not stupid either. Alchemists noticed that substances transform, that some transformations can be reversed and others cannot, that heat and mixture matter. Chemistry kept all of that. What astronomy and chemistry did was take the observations and give them a mathematics and an experimental method, and once that was done the older discipline had nothing left to say. Nobody consults an astrologer about the orbit of Mars.

The philosophy of language is in the same position today with respect to word embeddings, and Wittgenstein is its most interesting alchemist.

## What Wittgenstein Got Right

In the *Philosophical Investigations* Wittgenstein tore down the classical picture in which a word is a label attached to a fixed idea or a Platonic essence. In its place he put a slogan that has held up well: the meaning of a word is its use in the language. Words get their meaning from their deployment in the countless rule-governed activities he called language-games, ordering, describing, joking, guessing, all embedded in shared forms of life. And categories in natural language, he noticed, have no essence. There is no property common to everything we call a game. There is instead an overlapping web of similarities, which he called family resemblance.

This is a genuine observation, on a par with noticing that the planets wander against the fixed stars. Meaning does come from use. Categories are graded and fuzzy. Anyone who builds a theory of meaning that ignores these facts will build a wrong one.

## Where He Threw Up His Hands

Then Wittgenstein did what the alchemists did. Having made the observation, he declared it beyond systematic treatment. Because language is an open-ended, shifting collection of games, he argued, any attempt to build an explanatory theory of meaning is a category error. Philosophy "can in the end only describe" the use of language. "We must do away with all explanation, and description alone must take its place." Philosophy's job was reduced to therapy: showing the fly the way out of the fly-bottle by pointing out that its metaphysical problem was a grammatical confusion.

This is not a modest position. It is a strong empirical claim, that the phenomenon of meaning cannot be modelled, dressed up as humility. And it was made from an armchair, by a man who had collected no data, run no experiment, and formalised nothing. That is exactly the epistemic position of the astrologer who insists that the influence of Saturn on temperament is too subtle for arithmetic.

## The People Who Did the Arithmetic

While philosophers argued about "use" in seminars, linguists of a different temperament made it measurable. Zellig Harris and J. R. Firth stated the distributional hypothesis: you shall know a word by the company it keeps. That sentence looks like Wittgenstein's slogan, but it is doing something Wittgenstein refused to do. It says what "use" is. Use is the statistical distribution of the contexts in which a word occurs, and a distribution over a large enough corpus is a thing you can count.

Word2Vec, GloVe and their successors turned the counting into geometry. Each word became a dense vector in a space of a few hundred to a few thousand dimensions, and nobody chose the coordinates. They were learned by optimising a prediction task over billions of words of real text. I have written separately about [what these vectors are and why they need so many dimensions](@/blog/word_embeddings_arbitrariness_of_the_sign.en.md); the point here is what they did to the philosophical claims.

## Every Wittgensteinian Mystery Became a Computation

**Family resemblance** was supposed to be the barrier to formalisation. In vector space it is the default. A concept is a region, membership in it is a distance, and "game" sits near "sport", "competition", "puzzle" and "match" with no essence required and no sharp boundary anywhere. The thing Wittgenstein said could not be captured by a definition is captured perfectly well by a metric. He was right that definitions do not work. He was wrong that definitions were the only alternative.

**Irregularity** was supposed to make language unfit for mathematics. Then it turned out that king minus man plus woman lands next to queen, and Paris minus France plus Japan lands next to Tokyo. Gender, plurality, tense, the capital-of relation, comparative degree, all appear as roughly linear offsets that nobody put there. Philosophers spent centuries analysing analogy as a concept. It is vector subtraction.

**Language-games**, the claim that the same word means different things in different activities, was the last refuge. Static embeddings did have one vector per word, and the critics said so. Contextual models removed the objection: "bank" in "river bank" and "bank" in "investment bank" now receive different vectors, computed by attention over the surrounding tokens. The local game altering the word's meaning is not a mystery to be described. It is a function that is evaluated.

## Why This Is Obsolescence and Not Just Progress

It would be generous to say that embeddings continue Wittgenstein's programme. They do not. His programme was that no such thing could exist. Put the two side by side. Method: introspection about one's own linguistic intuitions, against statistical learning over corpora with an objective loss function. Treatment of use: an unquantifiable social custom, against a measurable probability distribution. Definitions: an impassable barrier, against graded clusters. Predictive power: none, against benchmarks on analogy, similarity and classification. Practical output: dissolved seminar paradoxes, against machine translation, search and every conversational agent in existence.

That table is the same table you could draw for astrology and astronomy in 1700. One column has the insight and the other has the science, and once the second column exists the first column is history of ideas.

Wittgenstein's confusions, the ones his therapy was meant to sweep away, had a cause he could not see. They came from trying to analyse a high-dimensional statistical phenomenon with low-dimensional prose. The fly-bottle was natural language itself, used as the instrument of analysis. Linear algebra was the way out, and it was not found by describing more carefully.

## The Lesson

I have argued before that [philosophy as practised fails](@/blog/why_philosophy_fails.en.md) because it never fixes its terms. The philosophy of language is the strongest possible case, because here philosophy had the right intuition and still produced nothing, while engineers with the same intuition and a loss function produced a working science of meaning in a decade. Meaning is use. Wittgenstein said it; Mikolov measured it. The difference between those two verbs is the difference between alchemy and chemistry, and in the study of meaning the transition has already happened. Speculative philosophy of language has run its course, superseded by tools that actually work.
