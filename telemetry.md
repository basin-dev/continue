# Telemetry

## How it works

- We use Segment to record telemetry about user actions
- At the moment, we only record client-side events
- This data is sent to a Google BigQuery data warehouse
- You can query this data using the Trevor.io tool

## What we track

### Event

Every time a user takes an action that triggers one of the event types below,
we record the VS Code machine ID, time of the event, and the type of event as
well as some additional metadata for some of the events.

### Event types

#### DebugSessionStarted

Recorded when a debug session is started. At the moment,
this event is not tracked.

#### DebugSessionStopped

Recorded when a debug session is stopped. At the moment,
this event is not tracked.

#### ExtensionActivated

Recorded when the VS Code extension is activated.

#### SuggestionAccepted

Recorded when a code fix suggestion is accepted.

#### SuggestionRejected

Recorded when a code fix suggestion is rejected.

#### UniversalPromptQuery

Recorded when a user asks a question to the prompt opened by `cmd+shift+j` 
on MacOS or `ctrl+shift+j` on Windows. It includes what question was asked.

#### ExplainCode

Recorded when the `Explain Code` button is clicked.

#### GenerateIdeas

Recorded when the `Generate Ideas` button is clicked.

#### SuggestFix

Recorded when the `Suggest Fix` button is clicked.

#### CreateTest

Recorded when the `Create Test` button is clicked.

#### AutoDebugThisTest

Recorded when the `AutoDebug This Test` button is clicked.

### Future Ideas

Server side
- Collect the programming langauge
- Collect the stack trace
- Collect the bug description
- Collect the code that was selected

Client side
- Collect `Enable Highlight` button clicked
- Collect `Disable Highlight` button clicked
- Collect the files that were edited
- Collect the final state of the code