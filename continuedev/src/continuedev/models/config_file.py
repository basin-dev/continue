from pydantic import BaseModel
from typing import List

class LLMPluginConfig(BaseModel):
	provider: str
	api_key: str

class FileSystemConfig(BaseModel):
	root: str

class ContinueAgentConfig(BaseModel):
	llm: LLMPluginConfig
	actions: List[str]
	validators: List[str]
	filesystem: FileSystemConfig