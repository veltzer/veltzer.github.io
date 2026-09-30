+++
title = "Email for Your Own Domain With Postfix"
date = 2011-10-02

[taxonomies]
tags = ["linux", "sysadmin", "self-hosting"]
+++

Running mail for your own domain is less mysterious than it looks, as long as you keep the goal modest: receive mail addressed to your domain, deliver it to a real local user, and reject everything for people who do not exist. This is the configuration I use, with Postfix as the mail server and SpamAssassin filtering. I am not going to cover sending reputation, DKIM and SPF here, which are their own subject; this is the receiving side.

## Install

```bash
sudo apt-get install postfix spamassassin spamass-milter
```

When Postfix's installer asks, choose "Internet Site" and give it your domain.

## The Core of main.cf

The whole behaviour lives in `/etc/postfix/main.cf`. The lines that matter:

```text
myhostname = mail.example.com
mydomain = example.com
myorigin = $mydomain
mydestination = $myhostname, $mydomain, localhost

# Deliver to local Unix users.
local_recipient_maps = proxy:unix:passwd.byname $alias_maps

# Reject mail for unknown users at the door, not after accepting it.
smtpd_recipient_restrictions =
    permit_mynetworks,
    reject_unauth_destination,
    reject_unknown_recipient_domain
```

The important decision is that last block. **Reject mail for non-existent users during the SMTP conversation, before you have accepted it.** If you accept first and discover the user does not exist later, you are obliged either to send a bounce (which, for spam with a forged sender, means you are spamming an innocent third party) or to drop it silently (which loses real mail sent to a typo). Rejecting up front makes the sending server deal with its own mistake.

## Aliases: One Real Mailbox Behind Many Names

You do not want a Unix account for every address. You want the standard role addresses to land in your own inbox. That is what `/etc/aliases` is for:

```text
root:       mark
postmaster: mark
webmaster:  mark
abuse:      mark
hostmaster: mark
mark:       mark
```

Every message to `root@`, `postmaster@`, `webmaster@` and the rest is funnelled to the real administrative user, who is not root. After editing the file you must compile it into the database Postfix actually reads:

```bash
sudo newaliases
```

Forgetting `newaliases` is the classic mistake: you edit `/etc/aliases`, nothing changes, because Postfix reads `/etc/aliases.db`, which `newaliases` regenerates. RFC convention requires that `postmaster` and `abuse` work on any domain that sends mail, so set those two even if you set nothing else.

## SpamAssassin

`spamass-milter` hands each incoming message to SpamAssassin before delivery. Enable it in `/etc/default/spamassassin` and point Postfix at the milter in `main.cf`:

```text
smtpd_milters = unix:/var/spool/postfix/spamass/spamass.sock
```

SpamAssassin scores each message and tags or rejects it above a threshold you set. Let it learn from your own mail with `sa-learn` and it improves.

## Test It

```bash
echo "test" | mail -s "hello" mark@example.com
sudo tail -f /var/log/mail.log
```

Watch the log as the message arrives, gets scored, and is delivered. Then send to an address that does not exist and confirm it is rejected at the SMTP stage rather than accepted and bounced.

That is the whole receiving setup: a domain that accepts mail for its real users, funnels the role accounts to you, and turns strangers' mistakes away at the door instead of taking them in and cleaning up afterward.
