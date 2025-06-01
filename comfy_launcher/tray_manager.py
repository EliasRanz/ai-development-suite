import threading
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image # pystray uses Pillow for icon image manipulation
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from logging import Logger
    from .gui_manager import GUIManager
    from .server_manager import ServerManager
    # from .config import Settings # If needed directly

class TrayManager:
    def __init__(self, app_name: str, assets_dir: Path, logger: 'Logger'):
        self.app_name = app_name
        self.assets_dir = assets_dir
        self.logger = logger
        self.icon: Optional[TrayIcon] = None
        self._thread: Optional[threading.Thread] = None

        # Placeholder for future interactions
        self.gui_manager: Optional['GUIManager'] = None
        self.server_manager: Optional['ServerManager'] = None

    def _create_menu(self) -> TrayMenu:
        """Creates the context menu for the tray icon."""
        # For now, these actions don't do anything.
        item_show_hide = TrayMenuItem("Show/Hide Window", lambda: self.logger.info("Tray: Show/Hide clicked (no action yet)"), enabled=False)
        item_quit = TrayMenuItem("Quit", lambda: self.logger.info("Tray: Quit clicked (no action yet)"), enabled=False)
        
        return TrayMenu(item_show_hide, item_quit)

    def run(self):
        """Starts the tray icon in its own thread."""
        self.logger.info("TrayManager: Initializing tray icon...")
        try:
            # You'll need a simple icon file (e.g., icon.png) in your assets directory
            # For pystray, it's best to use a .png or .ico
            icon_path = self.assets_dir / "icon.png" # Make sure you have an 'icon.png'
            if not icon_path.exists():
                self.logger.error(f"Tray icon asset not found at {icon_path}. Cannot start tray icon.")
                # Fallback: pystray can create a default icon if no image is provided, but it's ugly.
                # For a better experience, ensure an icon file exists.
                image = Image.new('RGB', (64, 64), color = 'red') # Placeholder if icon is missing
            else:
                image = Image.open(icon_path)

            self.icon = TrayIcon(self.app_name, image, self.app_name, self._create_menu())
            self.logger.info("TrayManager: Starting tray icon event loop...")
            self.icon.run() # This is blocking, so it runs in its own thread
            self.logger.info("TrayManager: Tray icon event loop finished.")
        except Exception as e:
            self.logger.error(f"TrayManager: Failed to run tray icon: {e}", exc_info=True)

    def start(self):
        """Starts the tray icon manager in a daemon thread."""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True, name="TrayIconThread")
            self._thread.start()
            self.logger.info("TrayManager: Thread started.")

    def stop(self):
        """Stops the tray icon."""
        self.logger.info("TrayManager: Stopping tray icon...")
        if self.icon:
            self.icon.stop()
        if self._thread and self._thread.is_alive():
            self.logger.debug("TrayManager: Waiting for tray thread to join...")
            self._thread.join(timeout=2) # Give it a moment to stop
            if self._thread.is_alive():
                self.logger.warning("TrayManager: Tray thread did not join cleanly.")
        self.logger.info("TrayManager: Tray icon stopped.")

    # --- Methods to be implemented later for actions ---
    # def set_managers(self, gui_manager: 'GUIManager', server_manager: 'ServerManager'):
    #     self.gui_manager = gui_manager
    #     self.server_manager = server_manager

    # def on_quit_selected(self):
    #     self.logger.info("Quit selected from tray menu.")
    #     # This will eventually call a global shutdown function or signal the main thread
    #     if self.icon:
    #         self.icon.stop() # Stop the tray icon first
    #     # Call main application shutdown logic here

    # def on_show_hide_selected(self):
    #     self.logger.info("Show/Hide selected from tray menu.")
    #     # This will call self.gui_manager.toggle_window() or similar