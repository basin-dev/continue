def load_validator_plugin(config: ValidatorPluginConfig) -> Validator:
	if config.name == "continue.tb_validator":
		return PythonTracebackValidator(config.cmd, config.cwd)
	elif config.name == "continue.pytest_validator":
		return PytestValidator(cwd=config.cwd)
	else:
		raise KeyError("Unknown validator plugin name")

def load_llm_plugin(config: LLMPluginConfig) -> LLM:
	if config.provider == "openai":
		return OpenAI(api_key=config.api_key)
	else:
		raise KeyError("Unknown LLM provider: " + config.provider)