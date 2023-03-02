import segment.analytics as analytics
from enum import Enum

analytics.write_key = '57yy2uYXH2bwMuy7djm9PorfFlYqbJL1'

class TelemetryEvent(str, Enum):
    CODE_EXPLAINED = "CodeExplained"
    IDEAS_GENERATED = "IdeasGenerated"
    FIX_SUGGESTED = "FixSuggested"
    TEST_CREATED = "TestCreated"
    DOCSTRING_GENERATED = "DocstringGenerated"

def send_telemetry_event(event, userid: str, properties=None):
    analytics.track(
        event=event,
        user_id=userid,
        properties=properties
    )