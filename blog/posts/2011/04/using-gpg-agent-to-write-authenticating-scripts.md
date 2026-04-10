---
tags:
  - gpg
  - security
  - linux
date: 2011-04-30
---

# Using gpg-agent to write authenticating scripts

Sometimes you want to write a shell or other script, and that script is going to have to run under `sudo`. Under such conditions if the script does anything that requires authentication it will not act as expected. In plain terms it means that the regular popup for authentication will not appear. The tool maybe written in a way which deals with the problem and falls back on other authentication methods, and yet it may not. In any case what you really want is for your own authentication agent (the little program called `gpg-agent` which is running on almost every Linux distribution from the time you log in till the time you log out) will do the authentication. This saves you lots of clicking. Imagine that the script has to do something which requires authentication X number of times. If the script does not use an agent it will not be able to cache the pass-phrases and so you will have to retype the pass-phrase several times. It can also be the case that your authenticating agent already has your pass-phrase in it's cache and you can save typing it yet another time.

Ok. So how do you do it? Well, in your original environment you have a variable called `GPG_AGENT_INFO`. This variable holds the details of how to connect to your authenticating agent. If you are running regular scripts then this variable, which is an environment variable, is automatically available to them. But if you run your scripts via `ssh` or `sudo` then it is not. Just make the variable available to those scripts. Obviously the users that these scripts will be running under will have to have the right level of permission to talk to your gpg agent. How do you make them available? One way is to pass this variable over the command line and turn it into an environment variable as soon as the script starts.
