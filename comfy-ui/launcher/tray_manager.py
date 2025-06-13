import threading
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import logging # Import logging for logger type hint if not already

if TYPE_CHECKING:
    from logging import Logger # Use standard Logger for type hint
    from .gui_manager import GUIManager
    # from .server_manager import ServerManager # Not directly used by TrayManager actions yet
    # from .config import Settings
from . import event_publisher, AppEventType # Import the global event publisher

class TrayManager:
    def __init__(self, app_name: str, assets_dir: Path, logger: 'Logger',
                 shutdown_event: threading.Event, gui_manager: 'GUIManager'):
        self.app_name = app_name
        self.assets_dir = assets_dir
        self.logger = logger
        self.icon: Optional[TrayIcon] = None
        self._thread: Optional[threading.Thread] = None
        self._shutdown_event = shutdown_event
        self._gui_manager = gui_manager
        # self.server_manager: Optional['ServerManager'] = None # Keep if needed later

        event_publisher.subscribe(AppEventType.APPLICATION_QUIT_REQUESTED, self.handle_application_quit_request)
        event_publisher.subscribe(AppEventType.GUI_WINDOW_HIDDEN, self.handle_gui_window_hidden)


    def _on_quit_selected(self):
        self.logger.info("Tray: Quit selected. Setting global shutdown event and publishing APPLICATION_QUIT_REQUESTED event.")
        self._shutdown_event.set() # Signal background threads and main thread loop
        event_publisher.publish(AppEventType.APPLICATION_QUIT_REQUESTED)
        # The GUIManager will be signaled via the published event.
        # self.icon.stop() will be handled by this class's own handler for APPLICATION_QUIT_REQUESTED.

    def handle_application_quit_request(self):
        """Handler for APPLICATION_QUIT_REQUESTED event to stop the tray icon."""
        self.logger.info("Handler: APPLICATION_QUIT_REQUESTED received by TrayManager. Stopping tray icon.")
        if self.icon:
            self.icon.stop() # Stop the tray icon itself
        # This handler's job is to stop the icon. The run() method publishes TRAY_MANAGER_SHUTDOWN_COMPLETE when its loop ends.

    def _create_menu(self) -> Optional[TrayMenu]:
        if not TrayMenu or not TrayMenuItem:
            self.logger.warning("pystray.Menu or MenuItem not available. Cannot create menu.")
            return None
        item_quit = TrayMenuItem(
            "Quit Application", # More descriptive
            self._on_quit_selected,
            enabled=True # Enable this action
        )
        return TrayMenu(item_quit)

    def run(self):
        self.logger.info("Initializing tray icon...")
        try:
            icon_path = self.assets_dir / "icon.png"
            if not icon_path.exists():
                self.logger.error(f"Tray icon asset not found at {icon_path}. Using fallback red square.")
                image = Image.new('RGB', (64, 64), color='red')
            else:
                image = Image.open(icon_path)

            menu = self._create_menu()
            if not menu: # If menu creation failed (e.g., pystray components not available)
                self.logger.error("Failed to create tray menu. Cannot start tray icon.")
                return

            self.icon = TrayIcon(self.app_name, image, self.app_name, menu)
            self.logger.info("Starting tray icon event loop...")
            self.icon.run()
            self.logger.info("Tray icon event loop finished.")
            # Publish event indicating tray manager has completed its run phase
            event_publisher.publish(AppEventType.TRAY_MANAGER_SHUTDOWN_COMPLETE)
        except Exception as e:
            self.logger.error(f"Failed to run tray icon: {e}", exc_info=True)
            # If tray fails critically, we might want to signal shutdown to prevent a zombie app
            if not self._shutdown_event.is_set():
                 self.logger.info("Signaling app shutdown due to critical tray error.")
                 self._shutdown_event.set()


    def start(self):
        if not TrayIcon: # Check if pystray is available
            self.logger.warning("pystray.Icon not available. Tray icon will not be started.")
            return

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True, name="TrayIconThread")
            self._thread.start()
            self.logger.info("Thread started.")
        else:
            self.logger.info("Thread already alive.")


    def stop(self):
        self.logger.info("Stopping tray icon...")
        if self.icon:
            self.icon.stop()
        if self._thread and self._thread.is_alive():
            self.logger.debug("Waiting for tray thread to join...")
            self._thread.join(timeout=2)
            if self._thread.is_alive():
                self.logger.warning("Tray thread did not join cleanly.")
        self.logger.info("Tray icon stopped.")

    def handle_gui_window_hidden(self):
        """Handles the GUI_WINDOW_HIDDEN event to update the tray menu if needed."""
        self.logger.debug("TrayManager: GUI_WINDOW_HIDDEN event received. Updating menu.")
        if self.icon:
            self.icon.update_menu()
