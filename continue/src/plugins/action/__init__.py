import pluggy

hookimpl = pluggy.HookimplMarker("continue.action")
"""Marker to be imported and used in plugins (and for own implementations)"""