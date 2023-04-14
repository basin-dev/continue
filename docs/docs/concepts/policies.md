# Policies

- You can go pretty far, pretty fast just using NLI + Python Traceback Snooper
- But you can go further, faster if the policy can cause the autocompletition of many steps
- Today, that means creating a plugin that suggests steps and their ordering for a specific workflow
- But developers might veer off from the planned path with refinements, error fixing, etc.
- So probably need to be able to manually indicate if a suggested step is done or not necessary
- Allowing policy to know this and move on to next most likely step or set of steps

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