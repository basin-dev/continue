from typing import List
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import BaseModel, parse_file_as
from .llm import LLM
from ..models.config_file import ContinueAgentConfig
# from ..plugins.load import *
from ..plugins import get_plugin_manager
from pluggy import PluginManager
from .policy import DemoPolicy, Policy
from .steps import Step, StepParams, DoneStep, Runner
from .observation import Observation
from .llm.openai import OpenAI
import os
from dotenv import load_dotenv

class Agent(BaseModel):
    # history: History
    llm: LLM
    filesystem: FileSystem
    # pm: PluginManager
    active: bool
    policy: Policy

    # @staticmethod
    # def from_config_file(config_file_path: str) -> "Agent":
    #     config = parse_file_as(path=config_file_path, type=ContinueAgentConfig)

    #     return Agent(
    #         llm=load_llm_plugin(config.llm),
    #         filesystem=RealFileSystem(),
    #         policy=load_policy_plugin(config.policy)
    #     )
	
    def __init__(self, llm: LLM, filesystem: FileSystem, policy: Policy):
        self.llm = llm
        self.filesystem = filesystem
        # self.history = History(states=[], filesystem=filesystem)
        # self.pm = get_plugin_manager(use_plugins=plugins)
        self.active = False
        self.policy = policy

    def _new_runner(self):
        return Runner(self, depth=0)

    def run_from_step(self, step: Step, require_permission: bool=False):
        if self.active:
            raise RuntimeError("Agent is already running")
        self.active = True

        next_step = step
        runner = self._new_runner()
        # Make it a generator!
        while not (next_step is None or isinstance(next_step, DoneStep)):
            observation = runner.run(next_step) # Should the runner be the thing keeping track of history from outputs?
            next_step = self.policy.next(observation)

    def run_from_observation(self, observation: Observation):
        next_step = self.policy.next(observation)
        self.run_from_step(next_step)

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

class DemoAgent(Agent):
    def __init__(self, cmd: str):
        super().__init__(llm=OpenAI(api_key), filesystem=RealFileSystem(), policy=DemoPolicy(cmd))


# The goal of the FileDiff concept is to separate planning from acting within every step.
# This has fewer benefits if the next step can't continue without having made the actual edit.
# But it also helps with understanding reversibility.
# Constraining actions to register all of their side-effects, and to either provide a reversal function else automatically have it marked irreversible
# has the benefit that we can be more sure/strict about reversibility. It might make development a little harder, forces a bit of a paradigm.
# How does it work in nested steps?
# First one runs inner step, receives its plan, then can use this without applying, but won't usually be possible. For example if you want to vaildate by running
# the code, then you must first apply. This ruins the split automatically.