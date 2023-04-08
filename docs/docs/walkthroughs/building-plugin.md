# Building a plugin

What are the simple building blocks that developers can use to define their own workflow automation?
- Simplest: hook and a prompt, that’s all
- ideally, they say, I want to do this when this happens
- at deepest level, should be able to create validator class as plugin, that specifies when to kickoff their thing

If you get to that, see the `continue/src/plugins/step/libs` folder for examples. 

Essentially just copy that and write whatever code you want inside the function.