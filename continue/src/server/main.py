from fastapi import FastAPI, Depends, Header
from typing import Dict, List
from uuid import uuid4
from pydantic import BaseModel
from ..libs.main import Agent, Artifact, History, Action

app = FastAPI()

class Session:
	id: str
	agent: Agent
	def __init__(self, config_file_path: str):
		self.id = str(uuid4())
		self.agent = Agent.from_config_file(config_file_path)

sessions: Dict[str, Session] = {}

def session(x_continue_session_id: str = Header("anonymous")) -> Session:
	if x_continue_session_id not in sessions:
		raise KeyError("Session ID not recognized")
	return sessions[x_continue_session_id]

# For now, just one history, but later, one per workspace/branch?

class StartSessionBody(BaseModel):
	config_file_path: str

class StartSessionResp(BaseModel):
	session_id: str

# THIS IS ALL OUTDATED, DON'T FEEL COMPELLED TO KEEP ANY OF IT
# mostly doesn't even work

@app.post("/session")
def start_session(body: StartSessionBody) -> StartSessionResp:
	session = Session(body.config_file_path)
	sessions.append(session)
	
	return StartSessionResp(session.id)

@app.get("/history")
def get_history(session=Depends(session)) -> History:
    return session.agent.history

@app.post("/act")
def request_act(action: Action, session=Depends(session)):
	session.agent.act(action)
	return "Success"

@app.post("/artifacts")
def post_artifacts(artifacts: List[Artifact], session=Depends(session)):
	action = session.agent.router.next_action(artifacts)
	session.agent.run_and_check(action)
	return "Success"	





"""
Communication we might need:
- Server -> Client: Ask for permission to perform an action
- POST send an observation (like traceback) to kick off a new agent. It's policy will decide what to do with the observation.
- POST request to go back in time / edit a step
- POST request to directly run a specified action
- GET state/history/stuff. But might also want to sync through websockets. This and the permission thing will be slightly tricky
"""