from pydantic import BaseModel

class Observation(BaseModel):
    pass

class ValidatorObservation(Observation):
    passed: bool
