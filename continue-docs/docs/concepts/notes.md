# Notes

A central challenge of this library is representing things such that they can be viewed by the user even as the agent is taking actions. For example, writing to a file should optionally be viewable as a streaming text input into a VS Code text editor, or a command being run should be viewable in a VS Code terminal.

So for example, there might be "middleware" around the writing to file action.
This "middleware" is especially important as the step that lets the user approve an action before it happens.
