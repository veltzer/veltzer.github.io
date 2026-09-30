+++
title = "Basic Software Is Turning Into Academia, and the Corporations Have Not Noticed"
date = 2012-05-13

[taxonomies]
tags = ["open-source", "programming", "opinion"]
+++

Something is happening to the lower layers of software that the companies selling software have not understood, and I think the reason they have not understood it is structural rather than a matter of attention. The lower layers are becoming academia.

## What Academia Does With Knowledge

Consider how knowledge works in a university. A result is published. Anyone may read it, check it, cite it, and build the next result on top of it. Nobody pays for the theorem. The people who produced it are paid, but not per use, and the thing itself is a commons. Progress in the field is measured by how much gets built on top of how much, and the whole arrangement works because the cost of copying a result is zero and the value of a result rises with the number of people who use it.

Now look at an operating system kernel, a compiler, a database engine, a web server, a cryptographic library. Every one of these is now developed in exactly that way. The source is published. Anyone may read it, check it, fork it, and build on it. Contributors are paid by employers, universities, or nobody, but never per copy. Reputation flows to the people whose work gets built upon. The mailing list is the journal and the patch is the paper.

**The bottom of the software stack has adopted the epistemology and the economics of a science.** Not by anyone's decision. It happened because the material has the same properties knowledge has: zero marginal cost, rising value with adoption, and correctness that only many independent eyes can establish.

## Why It Happened to the Bottom First

Basic software is infrastructure. Everybody needs the same kernel, the same TCP stack, the same compiler. There is no competitive advantage in having a slightly different one; there is only cost. So the rational thing for every participant, including every corporation, is to share the base and compete above it.

That is precisely the logic of basic research. Nobody competes on having a private version of thermodynamics. You share the physics and compete on the engine.

The layer that is shared keeps rising. It started with the compiler and the kernel, moved to the web server and the database, and is moving now into frameworks, build systems, and whole platforms. Each year a little more of what used to be a product becomes a shared result that a product is built on.

## The Corporate Blind Spot

Here is the part I find genuinely interesting, and it is the reason for the post.

Large software corporations have shown a remarkable inability to think abstractly about what they are selling. Ask one what its product is and it will name a piece of software: this operating system, that office suite, this database. It sells copies. Its accounting, its legal department, its licensing, its sales force, and its sense of itself are all organised around the copy.

But the copy is the one thing that is becoming worthless. What has value is the thing the corporation cannot see because it is not a noun on a price list: the ability to run, integrate, support, extend, and guarantee. Those are services around a shared body of knowledge, which is what a university hospital sells around a shared body of medicine.

**A corporation that can only think in terms of units shipped cannot perceive a market in which the unit is free.** It sees the free software as theft or as a passing fashion, because in its ontology a thing without a price is a thing without value. Then it watches a competitor who never sold a copy of anything become the most important company in the industry, and it does not understand what happened.

The inability is not stupidity. It is the same effect I have described elsewhere in [how organisations select the people who run them](@/blog/organizational_freedom_cost.en.md): the people who rose to the top of a company that sells copies are the people who were best at selling copies. Abstract thinking about what the company really is was not what got anyone promoted.

## What Follows

If the analogy holds, a few predictions follow, and they are checkable.

The shared layer keeps rising and never falls back. Nobody re-privatises a result once it is in the commons, for the same reason nobody re-privatises a theorem.

The money moves to services, integration, hardware, and the layers above the commons, and the companies that survive are the ones that stop asking what they ship and start asking what they know how to do.

And the culture of the lower layers starts to look more like a research community than a trade: peer review, citation, reputation, disputes settled in public, and a certain contempt for the marketing department. Anyone who has read a kernel mailing list already knows this part is true.

The face of the industry is changing, and the change is not that software got cheaper. It is that the bottom of the stack stopped being an industry at all and became a discipline.
