+++
title = "The Fax Machine Should Have Died Decades Ago, and Why It Has Not Is the Interesting Part"
date = 2026-09-19

[taxonomies]
tags = ["technology", "opinion"]
+++

Somewhere in your country right now, a hospital is faxing a patient's records to another hospital. A court is accepting a document by fax that it would not accept by email. A government office has a fax number printed on its letterhead and a scanner on the desk next to the machine, so that the paper that arrives can be turned back into the image it was before it was sent.

The fax machine is the worst way to move a document that has been invented since the courier, and it is still here. Both halves of that sentence deserve attention.

## Why It Should Go

Start with what a fax actually does. It takes a document that almost certainly began life as a file, prints it, scans the print at low resolution in black and white, encodes the scan as audio, plays the audio down a telephone line, and prints the result at the other end, where somebody scans it again to get a file. Every step loses information. The result is a degraded picture of text that no computer can read without guessing, sent over a channel that costs money per minute and fails if the line is busy.

**Everything a fax does, email with an attachment does better on every axis**: fidelity, cost, speed, searchability, storage, delivery confirmation, and the ability to reach more than one recipient. Where the concern is security, a fax is worse still. It is unencrypted, it goes to whichever machine holds that number today, and it prints out onto a tray in a corridor where anyone may pick it up.

There is no technical argument for the fax. There has not been one for thirty years.

## Why It Stays

The persistence is the interesting question, and the answer is not that people are stupid. It is that the fax sits at the intersection of three forces that individually look reasonable.

**Legal habit.** In many jurisdictions a faxed signature acquired legal standing decades ago, through case law and regulation written when the fax was the newest thing. Email signatures arrived later and their standing was established piecemeal, unevenly and with caveats. So a lawyer who wants certainty reaches for the channel with the longest settled record, which is the worst channel available. The law does not prefer the fax. It has simply had longer to stop worrying about it.

**Institutional risk aversion.** Nobody in a hospital or a ministry has ever been blamed for sending a fax. Plenty of people have been blamed for sending an email to the wrong address or losing a laptop. The fax is a channel with no recent scandals attached, which in a bureaucracy is worth more than any technical merit. The person who proposes replacing it takes on a risk; the person who leaves it alone takes on none. I have written about [how organisations select for exactly this reluctance](@/blog/organizational_freedom_cost.en.md), and the fax is a small monument to it.

**The network effect running backwards.** A fax is only useful if the other side has one. As long as the courts, the insurers and the pharmacies keep theirs, the hospital must keep its own, and as long as the hospital keeps its own, the others see no reason to drop theirs. Each participant is behaving rationally given the others, and the collective result is that a technology nobody would adopt today cannot be abandoned by anyone.

## The Regulatory Layer

There is a fourth force that deserves its own paragraph, because it is the one that actively keeps the machine alive rather than merely failing to kill it.

In several countries, health and legal regulations name the fax specifically as an approved channel for sensitive documents and are silent about, or hostile to, email. The regulations were written by people who understood the fax and did not understand encryption, and they have not been revisited because revisiting them would require someone to take responsibility for the new rule. So a machine with no security is mandated on security grounds, and a channel with real security is forbidden on the same grounds, and everyone involved knows this is absurd and nobody is positioned to change it.

**This is the general pattern of which the fax is the comic instance.** A rule written for one era outlives the era, the people who could change it have no incentive to, and the cost is paid diffusely by everyone who must comply. I have made the same argument about [legislation as a form](@/blog/process_over_legislation.en.md), and about the [complaints every new technology attracts](@/blog/nostalgia_about_technology.en.md). The fax is what those two arguments look like when they meet in a hospital corridor.

## What Would Kill It

Not a better technology. The better technology has existed for a generation and has not killed it.

What would kill it is a decision, taken at the level of the rules rather than the level of the machine: that a signed, encrypted document sent electronically has at least the legal standing of a smudged page arriving by telephone, and that regulations naming specific technologies expire unless renewed. Make those two changes and the fax machines will be in the skip within a year, because nobody actually wants them. They are kept by rules, not by people.

Until then the machine hums on, printing degraded copies of documents that were already files, in institutions that know better, because the cost of knowing better is borne by whoever moves first.
