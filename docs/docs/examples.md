# Examples

## Plugins for potential users

- Marcin (dltHub): creating a dlt pipeline (instead of using chatgpt)
- Nick (Den): fixing errors / natural language refinements to code (instead of using chatgpt)
- Ray (UMich): creating plots for his papers (instead of using chatgpt)
- Ella (Airbyte): adding types to connector columns (instead of adding bypasses to tests)
- Anish (Ramp): creating unit tests (instead of manually doing it / failing to use chatgpt for it)
- Phil (W&B): adding W&B experiment tracking to your ML model code (instead of using chatgpt)
- Alan (Rasa): creating a rasa bot (instead of using chatgpt)
- Shukri (Weviate): debugging through many unfamiliar abstractions (instead of having to step through all with a debugger)

## Ideas for plug-ins

- I want to be able to give natural language commands to make changes to a file (where it waits for me to approve / reject)
- I want errors / exceptions to be automatically caught, explained, fixed, and tested in the loop (with reversibility if it went wrong)
- Building a dlt pipeline for any API source involves the same set of tasks, I want to be able to automate many of the (sub-) tasks (see here and here)
- Ella (software engineer at Airbyte) talked about how previously they often didn’t declare the column type for connectors, which their tests now require, so they had to add a bunch of bypasses because it would require human input to figure out the type (example workflow: model looks at names of columns, insinuates the type and add its, just asks you to review, human in the loop review and accept — maybe just through a PR review)
- I want to be able to open up GitHub issues while I am coding (select the files involved, code sections involved, my env details, and have the model explain based on a bit of input from me and have it open an issue with all of that on GitHub)
- Post on Stack Overflow for you
- When code errors out with a traceback, find important snippets and try to fix
- When they alter the signature of a function, update all usages
- When they add a new abstract to a parent class, implement in all child classes
- When they make an edit that causes type checker errors, fix these
- After making a fix, they see another error and automatically fix it
- Automatically write tests for new functions they write, then edit until the tests pass
- If generated JSON doesn’t pass type checker, read and fix the error
- Generating pytests
- Data labelling and classification tasks (https://twitter.com/jackclarkSF/status/1645221542148837376?s=20)
