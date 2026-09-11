+++
title = "Word Embeddings and the Arbitrariness of the Sign"
date = 2026-09-11

[taxonomies]
tags = ["philosophy", "programming", "epistemology", "science"]
+++

A friend building on an AI agent platform asked me a question that I have since heard from several engineers. The platform let him choose between two OpenAI embedding models, one producing vectors of 3,072 numbers and one producing 1,536. Why, he wanted to know, does a word need thousands of numbers? The Hebrew word for bird, ציפור, has five letters. Would a five-dimensional space not do? And if you need room for the inflections, birds and my bird and so on, maybe a few more?

The question is a good one, because the right answer to it is the first lesson of linguistics, and most of us never had that lesson.

## Meaning Is Not in the Letters

The intuition behind the question is that a word's representation should somehow be derived from the word itself: its spelling, its length, its root and its morphology. That intuition is completely wrong, and the reason it is wrong is over a century old.

Consider the word תפוח, apple. Is there any connection between those letters, or the sounds they stand for, and the crisp red or green fruit? None. Whoever first used the word did not extract its consonants from the fruit's skin. When Eliezer Ben-Yehuda coined עגבנייה for tomato, he picked a root and a pattern, and the pick was an invention. The only place in the universe where the relationship between עגבנייה and the red vegetable exists is inside the heads of Hebrew speakers who share the convention. Had the convention gone the other way, with apples called tomatoes and tomatoes called apples, not a single property of either fruit would be different.

This is what Ferdinand de Saussure called the arbitrariness of the sign. A word is a signifier, an arbitrary label, attached by social agreement to a signified, a concept. The label carries no information about the concept. That is not a defect of language; it is the essence of it. Onomatopoeia and a handful of sound-symbolic words are the exceptions that make the rule visible.

Once you see this, the letter-counting question dissolves. An embedding is not a representation of the word ציפור. It is a representation of the concept that Hebrew speakers happen to label ציפור and English speakers happen to label bird. The spelling never enters into it, and could not, because the spelling contains nothing to enter.

## Why So Many Dimensions

The second question is better and survives the first answer. A language has perhaps 50,000 to 150,000 words in active use, inflections included. Even a 3,072-dimensional space restricted to zeros and ones has 2^3072 distinct points, a number that dwarfs every word in every language that ever existed. If you only wanted to tell words apart, 17 bits would do, and 120 dimensions would be absurd overkill. So what are the other 2,950 for?

The answer is that telling words apart is not the goal. If it were, an integer ID would be enough, and that is exactly what a dictionary index is. The goal of an embedding is to place concepts in a space where distance means something: where bird sits close to eagle and far from queen, where king minus man plus woman lands near queen. The vector is not an identifier. It is a position, and the position is chosen so that geometric nearness matches semantic nearness.

That requirement is what eats the dimensions. Think of a large apartment into which dozens of suitcases arrive from different countries. You want the ones from France near each other, but also the ones with clothes near each other, and the ones belonging to the same family, and the ones going on to the same destination. Each criterion is an independent axis along which things must be close or far, and if you have only the floor to work with, the criteria fight. Two dimensions let you honour one or two of them. Satisfying thousands of independent similarity relations at once, without any two of them colliding, takes thousands of degrees of freedom. High dimensionality is not there to store the words. It is there to give the relations between the words room.

Nobody places the words by hand. The positions are learned from a very large corpus, by observing which words occur in the company of which others, and adjusting until words that keep similar company end up nearby.

## The Numbers Mean Nothing on Their Own

My friend then opened a vector and looked at it: 1,536 floating point numbers, all between roughly minus 0.1 and 0.1. What does the fifteenth one mean? Is it "has wings"? Is it "is an animal"?

It is neither, and not because the answer is secret. No single coordinate has a meaning that a human can name. The meaning of the vector lies entirely in its relation to every other vector: the angle it makes with each, the distance to each. Rotate the whole space and every number changes while every meaning stays exactly the same, because the angles and distances are preserved. Meaning in an embedding is purely differential.

That, too, is Saussure. His claim was that in language there are only differences, without positive terms: a word means what it means by virtue of the words it is not, by its place in the network of contrasts. The linguists were describing, in prose and from the armchair, a structure that the machine learning people rediscovered by gradient descent eighty years later. It is one of the more satisfying convergences I know of between a humanistic theory and an engineering result.

## What This Buys You in Practice

None of this is philosophy for its own sake. Embeddings are a technology in their own right, older than and independent of the large language models that now use them as an input layer. You can take a corpus, turn each passage into a vector, store the vectors in a database that supports nearest-neighbour search, and ask it for the passages closest to "royalty" or "Shakespeare". No generative model is involved. This is what retrieval-augmented generation does with a company's documents: index them as vectors, fetch the nearest ones to the question, and hand those to the model so that it answers from the documents rather than from its imagination.

It also explains why serious systems keep the old full-text search alongside the new vector search. The two fail in opposite ways. Lexical search over tokens finds exact part numbers, identifiers and code fragments, and fails on paraphrase and synonyms. Semantic search over vectors finds paraphrase and synonyms, and is hopeless at exact identifiers, precisely because it never looked at the letters. So production systems run both and merge the ranked results, typically with reciprocal rank fusion. The engineering decision to combine them is a direct consequence of the linguistic point: one index knows the signifier and the other knows the signified, and you need both.

## The Lesson

Engineers who never took a linguistics course arrive at embeddings with the intuition that meaning lives in the string. It does not. It lives in the network of relations between concepts, and the string is an arbitrary handle that a community agreed to attach to one node of that network. Once that is understood, every design choice in an embedding model, the size of the vectors, the meaninglessness of individual coordinates, the need for a second lexical index, follows naturally. Lesson one of linguistics turns out to be lesson one of vector search.
