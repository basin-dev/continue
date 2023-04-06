from typing import List
from ..models.main import EditDiff
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import parse_file_as
from .llm import LLM
from .main import Artifact, History, Router, Validator, ActionParams, Action, HistoryState
from ..models.config_file import ContinueAgentConfig
from ..plugins.load import *
from ..plugins import get_plugin_manager
from pluggy import PluginManager

class BasicRouter(Router):
    def next_action(self, artifacts: List[Artifact]) -> Action | None:
        traceback = None
        for artifact in artifacts:
            if artifact.artifact_type == "traceback":
                traceback = artifact.data
                break
        
        if traceback is None:
            return None

        return SolveTracebackAction(traceback)

class Agent:
    history: History
    llm: LLM
    filesystem: FileSystem
    router: Router
    pm: PluginManager

    # Agent should maybe have locks ( or filesystem )

    @staticmethod
    def from_config_file(config_file_path: str) -> "Agent":
        config = parse_file_as(path=config_file_path, type=ContinueAgentConfig)

        return Agent(
            llm=load_llm_plugin(config.llm),
            validators=[
                load_validator_plugin(validator_config)
                for validator_config in config.validators
            ],
            router=load_router_plugin(config.router),
            filesystem=RealFileSystem()
        )
	
    def __init__(self, llm: LLM, validators: List[Validator], filesystem: FileSystem, router: Router, plugins: List[str], max_runs_per_validator: int = 1):
        self.llm = llm
        self.validators = validators
        self.filesystem = filesystem
        self.router = router
        self.max_runs_per_validator = max_runs_per_validator
        self.history = History(states=[], filesystem=filesystem)
        self.pm = get_plugin_manager(use_plugins=plugins)

    def _get_action_params(self) -> ActionParams:
        return ActionParams(
            llm=self.llm,
            filesystem=self.filesystem
        )
    
    def _apply_action(self, action: Action) -> List[EditDiff]:
        edits = action.run(self._get_action_params())
        diffs = []
        for edit in edits:
            # Should replace this with something inherent to EditDiff, this is slow. Also, do you want to use real diffs, or this, which is better for making suggestions?
            if edit.replacement == self.filesystem.read_range_in_file(RangeInFile(filepath=edit.filepath, range=edit.range)):
                continue
            diffs.append(self.filesystem.apply_file_edit(edit))
        return diffs

    def act(self, action: Action):
        diffs = self._apply_action(action)
        self.history.add(HistoryState(action_taken=action, diffs=diffs))

    def _rerun_current_action(self):
        idx_in_history = self.history.current_state_idx

        diffs = self._apply_action(self.history.states[idx_in_history].action_taken)
        self.history.states[idx_in_history].diffs = diffs

    def rerun_from_state(self, idx_in_history: int):
        # To do this, you need to know the actions that were taken.
        # An interesting thing is if you run again and don't get the same errors.
        # So you need to know which actions were in response to fixing validation errors.

        # This is bad...there's too much intimate understanding between Agent and History
        self.history.revert_to_state(idx_in_history)

        for i in range(idx_in_history, len(self.history.states)):
            self._rerun_current_action()
            self.history.current_state_idx = i

    # Shouldn't it be able to run and check recursively? And keep track of the global number of loops?
    def run_and_check(self, action: Action) -> bool:
        """Run the agent, returning whether successful."""
        self.act(action)
        success = self.fix_validators()
        return success
    
    def fix_validator(self, validator: Validator) -> bool:
        i = 0
        passed = False
        while i < self.max_runs_per_validator and not passed:
            passed, artifact = validator.run(self.filesystem)
            print("------------- Validator: ", passed, artifact)

            if passed:
                passed = True
            else:
                # Run the action that can fix this artifact
                next_action = self.router.next_action([artifact])
                
                if next_action is None:
                    return False
                
                self._run_action(next_action)

                # Then the validator is rerun --^

        return passed

    def fix_validators(self) -> bool:
        """Attempt to run and fix all validators, returning whether successful."""
        # Should probably also return WHY it was unsuccessful
        a_validator_failed = False
        for validator in self.validators:
            passed = self.fix_validator(validator)
            if not passed:
                a_validator_failed = True
                break

        return a_validator_failed
    
    def print_history(self):
        for diff in self.history:
            print("---------------------------------")
            print(f"File: {diff.edit.filepath}\n{diff.edit.replacement}")
            print("---------------------------------")
