---
tags:
  - ssh
  - security
  - linux
date: 2010-09-06
---

# Configuring ssh server for pubkey + password authentication

In a struggle to secure my home computer I did battle with the ssh server once again to configure it "just the way I want it" (tm). I prefer pubkey + password since this ensures that if I lose the laptop/phone/whatever then the lucky finder will not find his/her way into my home computer.

So, without further fanfare here are various bits that need to be done.

**Configuring the ssh server**
edit `/etc/ssh/sshd_config` and use the following entries:
Protocol 2 # protocol 1 is outdated
PubkeyAuthentication yes # I want public key to be used for authentication (and possibly to be combined with a pass phrase)

And of course there a bunch of authentication protocols that are not needed:
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no
PasswordAuthentication no
UsePAM no

**Creating the keys**
Still on the server in the home folder of the user you want to login remotely with, create the private/public pair using `ssh-keygen -t dsa` in `~/.ssh` (the default location for ssh-keygen). You get two files: `id_dsa` (private key) and `id_dsa.pub` (public key).

I used `dsa` keys in this post and you can use `rsa` keys if you pass `-t rsa` to `ssh-keygen`.

In the same folder on the server create a file called `authorized_keys` which has the public key (it can just be a copy of `id_dsa.pub` but has the potential to contain many keys - possibly one per user that can connect to said account or one per roaming device).

When creating the key pair you will be prompted for a pass phrase. This is where you choose whether or not you will need a pass phrase (which acts as a password) in order to access this account. If you leave the pass phrase empty you're allowing key only access with no password which is dangerous since if anyone gets a hold of your roaming device he/she can access your account with no extra data.

**Distributing the keys**
Copy the private key `~/.ssh/id_dsa` to the roaming devices you want to access the server from (laptop, phone, whatever). If the roaming device is a Linux box then put the private key in the same location (`~/.ssh/id_dsa`) in the home folder of the user that wishes to access the server. If you are using some other ssl tool besides command line ssh on a Linux box to access the server then it should have a place where you plug the private key into. If it doesn't have such a place then dump it. Putty (a widely used ssh client on windows) has an option to use a private key for connection.

**Note:**
While trying this out a lot of people seem to fail because they do all the experimentation on a desktop. In a desktop there is a system called `ssh-agent` which does the authentication for you in order to save you typing the same password multiple times. This agent is a problem when doing experimentation since it needs to be notified that you switched keys. So, every time you switch keys (regenerate the `~/.ssh/{id_dsa,id_dsa.pub}` files) you need to run `ssh-add` to let the agent know this. Another option is not do all of the experimentation from a desktop but rather from a login shell (`Ctrl+Alt+1` or whatever) so that the agent does not come into the game (which is complicated enough without it). Only after everything is setup re login to the graphical desktop and try everything out.
