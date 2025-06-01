import threading
from enum import Enum, auto
from collections import defaultdict
from typing import Callable, DefaultDict, List, Any
import logging

# Get a logger for the event system itself.
# It's good practice to use __name__ for module-level loggers.
event_system_logger = logging.getLogger(__name__)

class AppEventType(Enum):
    """Defines the types of events that can be published within the application."""
    # GUI Lifecycle
    GUI_WINDOW_CONTENT_LOADED = auto()  # Fired when the initial loading.html is fully loaded
    GUI_WINDOW_HIDDEN = auto()          # Fired when the GUI window is hidden (e.g., on close attempt)
    GUI_WINDOW_SHOWN = auto()           # Fired when the webview window becomes visible

    # Application Lifecycle
    APPLICATION_QUIT_REQUESTED = auto()     # Fired when a quit is initiated (e.g., from tray)
    APPLICATION_CRITICAL_ERROR = auto()     # Fired for critical errors that should halt the app
    SERVER_STOPPED_UNEXPECTEDLY = auto()    # Fired if the ComfyUI server process terminates unexpectedly

    # Shutdown Phase Events - Published by components when their cleanup is done
    APP_LOGIC_SHUTDOWN_COMPLETE = auto()
    TRAY_MANAGER_SHUTDOWN_COMPLETE = auto()
    # GUI_MANAGER_SHUTDOWN_COMPLETE is implicitly handled by webview.start() returning in the main thread.
    # If GUIManager had its own thread for complex shutdown, an event would be useful.
    
    # Events for testing the event system itself
    TEST_EVENT_NO_ARGS = auto()
    TEST_EVENT_WITH_ARGS = auto()

    # Tray/Window Interaction
    SHOW_WINDOW_REQUEST = auto() # Fired by tray to request GUI to show window
    # SHOW_WINDOW_REQUEST_RELAYED_TO_GUI = auto() # Fired by GUIManager if it processes the request

class EventPublisher:
    """A simple publish-subscribe event publisher."""
    def __init__(self):
        self._subscribers: DefaultDict[AppEventType, List[Callable[..., Any]]] = defaultdict(list)
        self._lock = threading.Lock() # To ensure thread-safe modification of subscribers

    def subscribe(self, event_type: AppEventType, handler: Callable[..., Any]):
        """Subscribes a handler function to a specific event type."""
        with self._lock:
            event_system_logger.debug(f"Subscribing handler '{getattr(handler, '__name__', repr(handler))}' to event '{event_type.name}'")
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: AppEventType, handler: Callable[..., Any]):
        """Unsubscribes a handler function from a specific event type."""
        with self._lock:
            try:
                self._subscribers[event_type].remove(handler)
                event_system_logger.debug(f"Unsubscribing handler '{getattr(handler, '__name__', repr(handler))}' from event '{event_type.name}'")
            except ValueError:
                event_system_logger.warning(f"Handler '{getattr(handler, '__name__', repr(handler))}' not found for event '{event_type.name}' during unsubscribe.")

    def publish(self, event_type: AppEventType, *args: Any, **kwargs: Any):
        """Publishes an event, calling all subscribed handlers."""
        handlers_to_call: List[Callable[..., Any]] = []
        with self._lock: # Make a copy of handlers to call, in case a handler tries to (un)subscribe during iteration.
            handlers_to_call = list(self._subscribers.get(event_type, []))

        event_system_logger.info(f"Publishing event '{event_type.name}' to {len(handlers_to_call)} subscriber(s). Args: {args}, Kwargs: {kwargs}")
        for handler in handlers_to_call:
            try:
                event_system_logger.debug(f"Calling handler '{getattr(handler, '__name__', repr(handler))}' for event '{event_type.name}'")
                handler(*args, **kwargs)
            except Exception as e:
                event_system_logger.error(f"Error in handler '{getattr(handler, '__name__', repr(handler))}' for event '{event_type.name}': {e}", exc_info=True)