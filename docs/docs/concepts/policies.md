# Policies

class MyPolicy(Policy):
  
  next(observation: Observation | None=None) ->
    Step:
      yield SetUpGPT4Step()
      requested_api = yield SelectAPIStep()
      yield InitPipelineStep(requested_api)
      
policies have to keep track of state

- given my history and set observations, next set of actions (how do I loop)
- same as RL, dialogue management
- nice and general, no special concept of validators, where you are running all of them every time
- makes things more flexible
- we just build out structure that is a subclass of that
- everything is a policy that calls an action and everything is an action
- sequential policy with validators

## DemoPolicy

This is the simplest policy I can think of. Will alternate between running and fixing code.