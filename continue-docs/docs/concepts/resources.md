# Resources

Resources represent objects that the AI has permission to act on. For example, you might specify a certain folder on which automated actions are allowed to take place.

Why not just give the AI access to a terminal where it can perform any action? This is potentially dangerous, as you don't want arbitrary code execution. Resources help you maintain a boundary around what you wish the AI to be able to tamper with. Constraining actions also ensures that every action can be reversible.

### Definition

Resources are defined by

1. a resource identifier,
2. a set of actions that can be taken on the resource,
3. a set of permissions that the AI must follow.
