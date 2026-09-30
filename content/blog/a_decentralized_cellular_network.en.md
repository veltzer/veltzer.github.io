+++
title = "A Cellular Network Nobody Owns Is Technically Easy and Politically Forbidden"
date = 2026-09-12

[taxonomies]
tags = ["technology", "politics"]
+++

Every phone in your pocket is a radio. Every one of them can talk to every other one within a few hundred metres. There are billions of them, densely packed exactly where people are. And yet to send a message to the person standing next to you, the message travels to a tower owned by a corporation, through that corporation's core network, and back to the tower, and you pay the corporation for the privilege.

I want to sketch how a network without the corporation would work, and then say why it does not exist, because the reason is not the one people assume.

## The Technical Sketch

A decentralised cellular network has three layers, and none of them requires an invention.

**The radio layer.** Phones talk directly to nearby phones, and to small fixed cells that people put on their windowsills and rooftops, over spectrum that anyone may use without a licence. That spectrum exists; it is what wireless networking and Bluetooth already run on, and more of it is available at higher frequencies. Range per hop is short, but hops are cheap and nodes are everywhere. This is a mesh, and meshes have been built many times, from community networks spanning whole cities to emergency systems that work when the towers are down.

**The routing layer.** A message finds its way across many hops without any central directory, the way the internet's routing was originally designed to work before it re-centralised. Nodes learn who their neighbours are, exchange what they know, and forward packets toward the destination. Where the mesh is thin, a node with a wired connection bridges to the ordinary internet. The protocols for this are decades old.

**The identity layer.** Nobody assigns you a number. Your identity is a cryptographic key you generate yourself, and people reach you by it. Messages are encrypted end to end by default, because there is no operator to trust and therefore no reason to leave anything in the clear. This, too, is built and running in several messaging systems today.

Put the three together and you have telephony, messaging and data among everyone in range of everyone, at no marginal cost, with no operator, no subscriber database, no central point at which to listen or to switch it off.

## Who Pays

The obvious objection is that networks cost money. Towers, backhaul, engineers. Who pays for a network with no owner?

Mostly, nobody needs to. The radios are already bought; they are in the phones. The fixed cells are cheap consumer hardware that people buy for the same reason they buy a wireless router. The expensive part of a conventional network, the core and the backhaul, largely disappears when traffic stays local, and most traffic is local.

Where a cost remains, for the bridges to the wider internet and for the nodes that carry more than their share, the settlement problem is exactly the one I described in [how cryptocurrency lets a decentralised organisation handle money](@/blog/crypto_funds_decentralized_organizations.en.md). A node that forwards your packets can be paid a fraction of a cent for doing so, automatically, by the protocol, with no company in the middle. The mechanism for paying strangers small amounts without an intermediary is the piece that was missing for decades and is missing no longer.

## Why It Does Not Exist

So the technology is available, the hardware is deployed, and the payment problem has a solution. Why do you pay a carrier?

**Because the spectrum that works well is licensed, and the licences were sold to the carriers.** The frequencies that travel far and penetrate walls, the ones that make a network good rather than merely possible, are allocated by the state to a handful of companies for enormous sums. Using them without a licence is a crime. The unlicensed bands are the leftovers: short range, crowded, and deliberately kept that way.

This is presented as physics. Spectrum is scarce, interference is real, somebody has to coordinate. All true, and all beside the point. Coordination does not require ownership, and it certainly does not require ownership by three companies. The mesh coordinates itself; that is what the protocols are for. The licensing regime was designed for a world of a few high-power transmitters and has been kept, long after that world ended, because it produces revenue for the state and monopoly rents for the licensees.

Add the second obstacle: the regulator's need to be able to listen. A network with no operator has no one to serve a warrant on, no database to subpoena, no switch to throw. Every state finds that intolerable, and every state has arranged that phones sold within its borders will not do what their radios could do.

**The network nobody owns is forbidden not because it would fail but because it would work**, and its working would remove a revenue stream, a rent, and a point of control simultaneously. That is three powerful constituencies against and a diffuse public for, which is the configuration in which the public loses every time.

## What Would Change It

Not a better protocol. The protocols are fine.

A decision, taken by the public rather than by the licensees and the regulator, that the spectrum is a commons and that the phones people buy will be permitted to use it. That is a political act, not an engineering one, and it is the kind of act a representative system finds nearly impossible, because the interested parties are concentrated, well funded and in the room, and the beneficiaries are everyone, which in that system means nobody.

I write this not because I expect the network to be built soon, but because it is useful to know precisely where the obstacle sits. It is not in the radio. It is in who was allowed to own the air.
