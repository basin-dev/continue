class Agent:
    def __init__(self, rsc_policy):
        self.rsc_policy = rsc_policy
        self.hooks = []
        
    def register_hook(self, hook):
        self.hooks.append(hook)
