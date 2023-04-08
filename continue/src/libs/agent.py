from typing import List
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import parse_file_as
from .llm import LLM
from ..models.config_file import ContinueAgentConfig
from ..plugins.load import *
from ..plugins import get_plugin_manager
from pluggy import PluginManager
from .policy import Policy

class Agent:
    history: History
    llm: LLM
    filesystem: FileSystem
    # pm: PluginManager
    active: bool
    policy: Policy

    @staticmethod
    def from_config_file(config_file_path: str) -> "Agent":
        config = parse_file_as(path=config_file_path, type=ContinueAgentConfig)

        return Agent(
            llm=load_llm_plugin(config.llm),
            filesystem=RealFileSystem(),
            policy=load_policy_plugin(config.policy)
        )
	
    def __init__(self, llm: LLM, filesystem: FileSystem, policy: Policy):
        self.llm = llm
        self.filesystem = filesystem
        self.history = History(states=[], filesystem=filesystem)
        # self.pm = get_plugin_manager(use_plugins=plugins)
        self.active = False
        self.policy = policy

    def run(self, step: "Step", require_permission: bool=False):
        next_step = step
        runner = Runner(self, depth=0)
        output = step(StepParams(filesystem=self.filesystem, llm=self.llm, runner=runner))
        # Make it a generator!
        next_step = self.policy.next()
        while isinstance(next_step, DoneStep):
            output = next_step(StepParams(filesystem=self.filesystem, llm=self.llm, runner=runner))
            next_step = self.policy.next()

    def run_from_observation(self, observation: Observation):
        self.history.states.append(observation)
        self.run(self.policy.next())