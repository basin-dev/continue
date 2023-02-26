import segment.analytics as analytics
from enum import Enum

analytics.write_key = '57yy2uYXH2bwMuy7djm9PorfFlYqbJL1'

class TelemetryEvent(str, Enum):
    CODE_EXPLAINED = "CodeExplained"
    IDEAS_GENERATED = "IdeasGenerated"
    FIX_SUGGESTED = "FixSuggested"
    TEST_CREATED = "TestCreated"
    DOCSTRING_GENERATED = "DocstringGenerated"

def send_telemetry_event(event, properties=None):

    analytics.track(
        event=event,
        userId=properties["vscode.env.machineId"],
        properties=properties
    )