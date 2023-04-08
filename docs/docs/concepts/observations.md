# Observations

## Events

Why observations?

## Artifacts

What is an artifact?
- a dumb name for anything it might return
- just has a type and some data
- I know this type of artifact and can solve it

## Resources

Resources represent objects that the AI has permission to act on. For example, you might specify a certain folder on which automated actions are allowed to take place.

Why not just give the AI access to a terminal where it can perform any action? This is potentially dangerous, as you don't want arbitrary code execution. Resources help you maintain a boundary around what you wish the AI to be able to tamper with. Constraining actions also ensures that every action can be reversible.

### Definition

Resources are defined by

1. a resource identifier,
2. a set of actions that can be taken on the resource,
3. a set of permissions that the AI must follow.

## Validators

What is a validator?
- See 1, 2, and 3 above
- it runs code, runs typechecker, linter, it will return an artifact
- better name, triggers, hooks, might be better, maybe separate concepts?
