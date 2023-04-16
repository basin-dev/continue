import time
from fastapi import FastAPI, Depends, Header, WebSocket, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
from uuid import uuid4
from pydantic import BaseModel
from uvicorn.main import Server
from ..libs.policy import DemoPolicy
from ..libs.steps.main import RunCodeStep, RunPolicyUntilDoneStep, UserInputStep
from ..libs.core import Agent, History, Step
from ..libs.observation import Observation
from dotenv import load_dotenv
from ..libs.llm.openai import OpenAI
from .ide_protocol import AbstractIdeProtocolServer
import os
import asyncio
import nest_asyncio
nest_asyncio.apply()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/notebook", tags=["notebook"])

# Graceful shutdown by closing websockets
original_handler = Server.handle_exit


class AppStatus:
    should_exit = False

    @staticmethod
    def handle_exit(*args, **kwargs):
        AppStatus.should_exit = True
        print("Shutting down")
        original_handler(*args, **kwargs)


Server.handle_exit = AppStatus.handle_exit


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

    def new_session(self, ide: AbstractIdeProtocolServer) -> str:
        cmd = "python3 /Users/natesesti/Desktop/continue/extension/examples/python/main.py"
        agent = Agent(llm=OpenAI(api_key=openai_api_key),
                      policy=DemoPolicy(cmd=cmd), ide=ide)
        session_id = str(uuid4())
        session = Session(session_id=session_id, agent=agent)
        self.sessions[session_id] = session

        def on_step(step: Step):
            print("Sending step to websocket", step)
            session_manager.send_ws_data(session_id, {
                "messageType": "history",
                "history": agent.history.dict()
            })

        agent.on_step(on_step)
        asyncio.create_task(agent.run_policy())
        return session_id

    def remove_session(self, session_id: str):
        del self.sessions[session_id]

    def register_websocket(self, session_id: str, ws: WebSocket):
        self.sessions[session_id].ws = ws
        print("Registered websocket for session", session_id)

    def send_ws_data(self, session_id: str, data: Any):
        if self.sessions[session_id].ws is None:
            print(f"Session {session_id} has no websocket")
            return

        async def a():
            print("Sending data to websocket", data,
                  self.sessions[session_id].ws)
            await self.sessions[session_id].ws.send_json(data)

        # Run coroutine in background
        if self._event_loop is None or self._event_loop.is_closed():
            print("Creating event loop")
            self._event_loop = asyncio.new_event_loop()
            self._event_loop.run_until_complete(a())
            self._event_loop.close()
        else:
            print("Using existing event loop")
            self._event_loop.run_until_complete(a())
            self._event_loop.close()


session_manager = SessionManager()


def session(x_continue_session_id: str = Header("anonymous")) -> Session:
    return session_manager.get_session(x_continue_session_id)


def websocket_session(session_id: str) -> Session:
    return session_manager.get_session(session_id)


class StartSessionBody(BaseModel):
    config_file_path: str | None


class StartSessionResp(BaseModel):
    session_id: str


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: Session = Depends(websocket_session)):
    await websocket.accept()

    session_manager.register_websocket(session.session_id, websocket)
    data = await websocket.receive_text()
    # Update any history that may have happened before connection
    await websocket.send_json({
        "messageType": "history",
        "history": session_manager.get_session(session.session_id).agent.history.dict()
    })
    print("Session started", data)
    while AppStatus.should_exit is False:
        data = await websocket.receive_json()

        if "messageType" not in data:
            continue
        messageType = data["messageType"]
        if messageType == "main_input":
            # Do something with user input
            asyncio.create_task(session.agent.accept_user_input(data["value"]))
        elif messageType == "reverse":
            # Reverse the history to the given index
            session.agent.history.reverse_to_index(data["index"])
    print("Closing websocket")
    await websocket.close()


@router.post("/run")
def request_run(step: Step, session=Depends(session)):
    """Tell an agent to take a specific action."""
    asyncio.create_task(session.agent.run_from_step(step))
    return "Success"


@router.get("/history")
def get_history(session=Depends(session)) -> History:
    return session.agent.history


@router.post("/observation")
def post_observation(observation: Observation, session=Depends(session)):
    asyncio.create_task(session.agent.run_from_observation(observation))
    return "Success"
