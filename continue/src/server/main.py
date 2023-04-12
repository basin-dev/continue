import time
from fastapi import FastAPI, Depends, Header, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
from uuid import uuid4
from pydantic import BaseModel
from ..libs.policy import DemoPolicy
from ..libs.steps.main import RunCodeStep, UserInputStep
from ..libs.core import Agent, History, Step
from ..libs.observation import Observation
from dotenv import load_dotenv
from ..libs.llm.openai import OpenAI
import os
import asyncio
import nest_asyncio
nest_asyncio.apply()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Session:
    session_id: str
    agent: Agent
    ws: WebSocket | None

    def __init__(self, session_id: str, agent: Agent):
        self.session_id = session_id
        self.agent = agent
        self.ws = None


class SessionManager:
    sessions: Dict[str, Session] = {}
    _event_loop: asyncio.BaseEventLoop | None = None

    def get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            raise KeyError("Session ID not recognized")
        return self.sessions[session_id]

    def add_session(self, agent: Agent) -> str:
        session_id = str(uuid4())
        session = Session(session_id=session_id, agent=agent)
        self.sessions[session_id] = session
        return session_id

    def remove_session(self, session_id: str):
        del self.sessions[session_id]

    def register_websocket(self, session_id: str, ws: WebSocket):
        self.sessions[session_id].ws = ws
        print("Registered websocket for session", session_id)

    def send_ws_data(self, session_id: str, data: Any):
        if self.sessions[session_id].ws is None:
            return

        async def a():
            print("Sending data to websocket", data,
                  self.sessions[session_id].ws)
            resp = await self.sessions[session_id].ws.send_text("hey")
        # Run coroutine in background
        if self._event_loop is None or self._event_loop.is_closed():
            print("Creating event loop")
            self._event_loop = asyncio.new_event_loop()
            self._event_loop.create_task(a())
            self._event_loop.run_forever()
        else:
            print("Using existing event loop")
            self._event_loop.create_task(a())


session_manager = SessionManager()


def session(x_continue_session_id: str = Header("anonymous")) -> Session:
    return session_manager.get_session(x_continue_session_id)


def websocket_session(session_id: str) -> Session:
    return session_manager.get_session(session_id)


class StartSessionBody(BaseModel):
    config_file_path: str | None


class StartSessionResp(BaseModel):
    session_id: str


cmd = "python3 /Users/natesesti/Desktop/continue/extension/examples/python/main.py"


@app.post("/session")
def start_session() -> StartSessionResp:
    """Create a new agent and return its ID"""
    agent = Agent(llm=OpenAI(api_key=openai_api_key),
                  policy=DemoPolicy(cmd=cmd))
    session_id = session_manager.add_session(agent)

    def on_step(step: Step):
        session_manager.send_ws_data(session_id, {
            "type": "history",
            "history": agent.history.json()
        })

    agent.on_step(on_step)
    return StartSessionResp(session_id=session_id)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: Session = Depends(websocket_session)):
    await websocket.accept()

    session_manager.register_websocket(session.session_id, websocket)
    time.sleep(3)
    session.agent.run_from_step(RunCodeStep(cmd=cmd))
    while True:
        data = await websocket.receive_text()
        print("Received data", data)

        if "type" not in data:
            continue
        messageType = data["type"]
        if messageType == "mainInput":
            # Do something with user input
            session.agent.run_from_step(
                UserInputStep(user_input=data["value"]))
        elif messageType == "moveInTimeline":
            # Reverse the history to the given index
            session.agent.history.move_to_index(data["index"])

    # data = await websocket.receive_text()  # Wait for acknowledgment

    # session_manager.register_websocket(session.session_id, websocket)
    # websocket.send_text("Connected to session")
    # session.agent.run_from_step(RunCodeStep(cmd=cmd))
    # while True:
    #     await websocket.send_text(f"Message JSON was: {data}")
    #     if "type" not in data:
    #         continue
    #     messageType = data["type"]
    #     if messageType == "mainInput":
    #         # Do something with user input
    #         session.agent.run_from_step(
    #             UserInputStep(user_input=data["value"]))
    #     elif messageType == "moveInTimeline":
    #         # Reverse the history to the given index
    #         session.agent.history.move_to_index(data["index"])

    #     data = await websocket.receive_text()
    #     print("Received data", data)


@app.post("/run")
def request_run(step: Step, session=Depends(session)):
    """Tell an agent to take a specific action."""
    session.agent.run_from_step(step)
    return "Success"


@app.get("/history")
def get_history(session=Depends(session)) -> History:
    return session.agent.history


@app.post("/observation")
def post_observation(observation: Observation, session=Depends(session)):
    session.agent.run_from_observation(observation)
    return "Success"

    # Send messages whenever there is an update to the history
    # ws.send_json(history)

# History - for now just a list
# History updates through websockets - do this later with RTK Query
# agent.run
# agent.run_from_observation
# agent.from_config_file, but for now just start with a default config
