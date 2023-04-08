# API

Client: notebook-like UI

Server: continue framework server

Send traceback to an endpoint that will kick off a new "loop" (is this what we want to call it? New "agent"?). This is the kind of thing that the agent did not ask for. Maybe a POST /observation endpoint or something.

If the agent is asking for something (e.g. it has decided to run the "type checker validator action"), then the server should probably just run the type checker on its own OR request to the VS Code extension to send over information that it has more readily available.

Server -> Client: Ask for permission to perform an action
POST send an observation (like traceback) to kick off a new agent. It's policy will decide what to do with the observation.
POST request to go back in time / edit a step
POST request to directly run a specified action
GET state/history/stuff. But might also want to sync through websockets. This and the permission thing will be slightly tricky

all state should be managed in continue, need to sync that really well, something we mgiht use for this, could generate that code from open API: https://redux-toolkit.js.org/rtk-query/usage/code-generation

discussing/researching how we will sync/communicate server/client

what is the agent?
what is the permission thing?
If we need two way communication, then it should most likely be through WebSockets
