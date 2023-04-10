from pydantic import BaseModel
from ..models.main import Traceback

class Observation(BaseModel):
    pass

# People can make new observations by making new pydantic types.
class TracebackObservation(Observation):
    traceback: Traceback

class ValidatorObservation(Observation):
    passed: bool
