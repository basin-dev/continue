from fastapi import FastAPI, Depends, Header, WebSocket
from typing import Dict, List
from uuid import uuid4
from pydantic import BaseModel
from ..libs.agent import Agent, DemoAgent
from ..libs.steps import Step
from ..libs.observation import Observation
from ..libs.history import History

app = FastAPI()

class AgentManager:
	agents: Dict[str, Agent] = {}

	def get_agent(self, agent_id: str) -> Agent:
		if agent_id not in self.agents:
			raise KeyError("Agent ID not recognized")
		return self.agents[agent_id]
	
	def add_agent(self, agent: Agent) -> str:
		agent_id = str(uuid4())
		self.agents[agent_id] = agent
		return agent_id
	
	def remove_agent(self, agent_id: str):
		del self.agents[agent_id]

agent_manager = AgentManager()

def agent(x_continue_agent_id: str = Header("anonymous")) -> Agent:
	return agent_manager.get_agent(x_continue_agent_id)

class StartAgentBody(BaseModel):
	config_file_path: str

class StartAgentResp(BaseModel):
	session_id: str

@app.post("/agent")
def start_agent(body: StartAgentBody) -> StartAgentResp:
	"""Create a new agent and return its ID"""
	agent = DemoAgent()
	agent_id = agent_manager.add_agent(agent)
	return StartAgentResp(agent_id)

@app.post("/run")
def request_run(step: Step, agent=Depends(agent)):
	"""Tell an agent to take a specific action."""
	agent.run_from_step(step)
	return "Success"

@app.get("/history")
def get_history(agent=Depends(agent)) -> History:
    return agent.agent.history

@app.post("/observation")
def post_observation(observation: Observation, agent=Depends(agent)):
	agent.run_from_observation(observation)
	return "Success"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.recieve_json()
        await websocket.send_text(f"Message JSON was: {data}")

		# Send messages whenever there is an update to the history
		# ws.send_json(history)
		
# History - for now just a list
# History updates through websockets - do this later with RTK Query
# agent.run
# agent.run_from_observation
# agent.from_config_file, but for now just start with a default config