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

    def _on_show_hide_window_selected(self):
        self.logger.info("Tray: Show/Hide Window clicked.")
        if self._gui_manager and self._gui_manager.webview_window:
            # pywebview doesn't have a direct is_visible or is_hidden property reliably across backends.
            # We'll try to use the 'hidden' attribute if available (pywebview 4.0+)
            # or just call show() which might toggle or bring to front.
            try:
                if getattr(self._gui_manager.webview_window, 'hidden', False): # Check if 'hidden' attr exists and is True
                    self._gui_manager.webview_window.show()
                    self.logger.info("Tray: Showing window.")
                else:
                    # If not hidden or 'hidden' attribute doesn't exist, try hiding.
                    # If it was already visible, this hides it. If it was hidden, this might do nothing or error.
                    # A more robust solution might involve GUIManager tracking its own visibility state.
                    self._gui_manager.webview_window.hide()
                    self.logger.info("Tray: Hiding window.")
            except Exception as e: # Catch potential errors if .hidden or .show/.hide misbehave
                self.logger.warning(f"Tray: Error toggling window visibility: {e}. Attempting to show.")
                try:
                    self._gui_manager.webview_window.show() # Fallback to just showing
                except Exception as e_show:
                    self.logger.error(f"Tray: Fallback show() also failed: {e_show}")
        else:
            self.logger.warning("Tray: GUI manager or window not available to show/hide.")


    def _on_quit_selected(self):
        self.logger.info("Tray: Quit selected. Signaling application shutdown.")
        self._shutdown_event.set()
        if self.icon:
            self.icon.stop()

    def _create_menu(self) -> Optional[TrayMenu]:
        if not TrayMenu or not TrayMenuItem:
            self.logger.warning("TrayManager: pystray.Menu or MenuItem not available. Cannot create menu.")
            return None
        
        item_show_hide = TrayMenuItem(
            "Show/Hide Window",
            self._on_show_hide_window_selected,
            enabled=True # Enable this action
        )
        item_quit = TrayMenuItem(
            "Quit Application", # More descriptive
            self._on_quit_selected,
            enabled=True # Enable this action
        )
        return TrayMenu(item_show_hide, item_quit)

    def run(self):
        self.logger.info("TrayManager: Initializing tray icon...")
        try:
            icon_path = self.assets_dir / "icon.png"
            if not icon_path.exists():
                self.logger.error(f"Tray icon asset not found at {icon_path}. Using fallback red square.")
                image = Image.new('RGB', (64, 64), color='red')
            else:
                image = Image.open(icon_path)

            menu = self._create_menu()
            if not menu: # If menu creation failed (e.g., pystray components not available)
                self.logger.error("TrayManager: Failed to create tray menu. Cannot start tray icon.")
                return

            self.icon = TrayIcon(self.app_name, image, self.app_name, menu)
            self.logger.info("TrayManager: Starting tray icon event loop...")
            self.icon.run()
            self.logger.info("TrayManager: Tray icon event loop finished.")
        except Exception as e:
            self.logger.error(f"TrayManager: Failed to run tray icon: {e}", exc_info=True)
            # If tray fails critically, we might want to signal shutdown to prevent a zombie app
            if not self._shutdown_event.is_set():
                 self.logger.info("TrayManager: Signaling app shutdown due to critical tray error.")
                 self._shutdown_event.set()


    def start(self):
        if not TrayIcon: # Check if pystray is available
            self.logger.warning("TrayManager: pystray.Icon not available. Tray icon will not be started.")
            return

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True, name="TrayIconThread")
            self._thread.start()
            self.logger.info("TrayManager: Thread started.")
        else:
            self.logger.info("TrayManager: Thread already alive.")


    def stop(self):
        self.logger.info("TrayManager: Stopping tray icon...")
        if self.icon:
            self.icon.stop()
        if self._thread and self._thread.is_alive():
            self.logger.debug("TrayManager: Waiting for tray thread to join...")
            self._thread.join(timeout=2)
            if self._thread.is_alive():
                self.logger.warning("TrayManager: Tray thread did not join cleanly.")
        self.logger.info("TrayManager: Tray icon stopped.")
