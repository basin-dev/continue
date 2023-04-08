from plugins import action
from ....libs.main import ActionParams

@action.hookimpl
def run(params: ActionParams):
    print("Hello World!")