---
tags:
  - git
  - gpg
  - security
date: 2010-07-03
---

# Git and signing

I'm now using git heavily for configuration management and wanted to sign my objects. There were no complete guides out there that I found so here is the list of instructions that I finally arrived at:

	- If you have a key that you are already using to sign things (email, code, whatever) then you can skip to item 4. If not, then decide on an name, email and pass phrase that you will use to sign your code.
	- Create a key pair based on the name, email and pass phrase that you chose,. You can do this using `gpg2 --gen-key`. The program is interactive and very easy to use. The program comes with the `gnupg2` package on Ubuntu or Debian. The keys are generated in `~/.gnupg`. If you want to see that everything went well the you can list all keys using `gpg2 --list-public-keys`.
	- Configure git to use your email. This usually involves editing your git configuration file at `~/.gitconfig` and setting the `email` config option under the `user` section to your email.
	- Sign your change when you commit or tag it. If you commit then use "git -s commit". If you tag then use "git tag -s -m 'commit message' [tagname]".
