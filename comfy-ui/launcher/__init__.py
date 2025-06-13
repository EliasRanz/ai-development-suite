"""
ComfyUI Launcher Package.
This __init__.py can be used to expose package-level objects.
"""
from .event_system import EventPublisher, AppEventType

event_publisher = EventPublisher()