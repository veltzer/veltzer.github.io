+++
title = "What Open Source Should Demand From Microsoft"
date = 2008-05-18

[taxonomies]
tags = ["open-source", "windows", "opinion"]
+++

Every few months Microsoft announces a new openness initiative, and every few months the open-source world debates whether to believe it. I think the debate is framed wrongly. The question is not whether Microsoft is sincere; a corporation is not the kind of thing that is sincere or insincere. The question is what, concretely, would have to be true for interoperability to be real, and whether those things are being delivered.

Here is my list. Each item is checkable, and each one matters for a reason I will give.

## Open Document Formats

The formats in which the world's documents are stored must be fully specified, freely implementable, and not controlled by one vendor. A format that only one product can read correctly is a lock on every file written in it.

This matters because documents outlive software. A letter written today should be readable in thirty years without a licence from anyone. The current situation, where the dominant office formats are specified after the fact, at enormous length, with behaviour that amounts to *do what our product does*, does not meet the bar. A specification nobody but the author can implement is not a specification.

## Documented Protocols

Every protocol the operating system and its server products speak on the network must be documented well enough that an independent implementation can be written from the document alone, without reverse engineering and without a licence agreement.

File sharing, authentication, directory services, mail. These are the roads of a network. When one vendor holds the only accurate map, every other vendor's product is a second-class citizen by construction, not because it is worse. The Samba project has spent years reverse engineering what should have been a public document, and the European Commission had to compel disclosure. Disclosure under compulsion is not openness.

## Patent Non-Assertion

A promise, legally binding and irrevocable, not to assert patents against implementations of the formats and protocols above, including implementations distributed under free licences.

Without this, every other item on the list is a trap. A documented format that infringes a patent the moment you implement it has been documented to draw you in, not to let you out. Vague statements about not suing *non-commercial* implementations do not help, because the free licences that matter make no such distinction and cannot.

## No OEM Exclusivity

Hardware manufacturers must be free to ship machines with another operating system, or with none, without losing the terms they get for the machines that ship with Windows.

This is the item people forget because it is not technical. But it is the one that decides whether any alternative can reach a user who has not already decided to go looking for it. A tax on every machine sold, paid whether or not the buyer wanted the software, is how a monopoly funds itself, and no amount of format openness compensates for it.

## Interoperability Tests, Run in the Open

Public test suites, and public results, showing that independent implementations of the formats and protocols actually work against Microsoft's own products.

A document that says *this is the protocol* is a claim. A test that a third party's server passes against a Windows client is evidence. Openness that cannot be tested is a press release.

## Why the List and Not Trust

I have deliberately written nothing here about intentions. Microsoft may well contain people who want all of this; large companies contain people who want everything. What the company does is determined by its interests, and its interest is to keep the lock while appearing to remove it.

**So the open-source world should stop asking whether Microsoft has changed and start asking which items on the list have been delivered.** That question has an answer at any given moment, it does not depend on anyone's sincerity, and it cannot be satisfied by an announcement.

If all five are delivered, the platform stops being a lock and becomes a product competing on merit, which is all anyone ever asked for. Until then, the correct response to the next openness initiative is to hold up the list and ask which line it crosses off.
