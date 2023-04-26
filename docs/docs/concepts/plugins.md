# Plugins

## How to run

Haven't determined how we want to run plugins, but I've done something Ad Hoc in the DemoPolicy where you just search for exact strings. You could instead search for the string with a slash before if you want it to be like a slash command (see below in policy.py)

Example plugins in libs/steps/main.py,nate.py

follows an interface, so that Continue knows how to find it and interact with it

Policy Plugins
Step Plugins
Validator Plugins

What are plugins?

Plugin is a more general word, which subsumes validator plugins, tool plugins, what else?

What are plugins?
- provide library to more easily define hooks for common use cases, watch when I make for this kind of edit, we do the harder work of understanding that file edit dealt with, what types of ast nodes is it editing, etc.
- https://pluggy.readthedocs.io/en/latest/
- did not push yet some of the changes, write someone elses python package with pip install, action, validators
- people making plugins
- some cli tool that makes it easy to do so