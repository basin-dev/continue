import pluggy

hookimpl = pluggy.HookimplMarker("continue.validator")
"""Marker to be imported and used in plugins (and for own implementations)"""