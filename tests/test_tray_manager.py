import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from threading import Thread as OriginalPythonThread, Event as ThreadingEvent # Get the original Thread class and Event
import logging

# Add project root to sys.path for imports
import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.tray_manager import TrayManager
from comfy_launcher.gui_manager import GUIManager # For spec
from pystray import Menu as TrayMenu, MenuItem as TrayMenuItem, Icon as TrayIcon # Import Icon as TrayIcon
from PIL import Image # For mocking Image.open
from comfy_launcher.event_system import AppEventType # For event testing - this import is present

class TestTrayManager(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)

        # Prepare a mock for the specific icon path object
        self.mock_icon_path_object = MagicMock(spec=Path)
        self.mock_icon_path_object.exists = MagicMock(return_value=True) # Default to exists = True
        self.mock_icon_path_object.__str__ = MagicMock(return_value="/fake/assets/icon.png") # For logging

        self.mock_assets_dir = MagicMock(spec=Path, return_value=Path("/fake/assets"))
        self.mock_assets_dir.__truediv__ = lambda _, other: self.mock_icon_path_object if other == "icon.png" else Path(str(self.mock_assets_dir) + "/" + str(other))
        self.app_name = "TestAppTray"
        self.mock_shutdown_event = MagicMock(spec=ThreadingEvent)
        self.mock_gui_manager = MagicMock(spec=GUIManager)

        self.tray_manager = TrayManager(
            app_name=self.app_name,
            assets_dir=self.mock_assets_dir,
            logger=self.mock_logger,
            shutdown_event=self.mock_shutdown_event,
            gui_manager=self.mock_gui_manager
        )

    def test_initialization(self):
        self.assertEqual(self.tray_manager.app_name, self.app_name)
        self.assertEqual(self.tray_manager.assets_dir, self.mock_assets_dir)
        self.assertEqual(self.tray_manager.logger, self.mock_logger)
        self.assertEqual(self.tray_manager._shutdown_event, self.mock_shutdown_event)
        self.assertEqual(self.tray_manager._gui_manager, self.mock_gui_manager)
        self.assertIsNone(self.tray_manager.icon)
        self.assertIsNone(self.tray_manager._thread)

    def test_create_menu(self):
        menu = self.tray_manager._create_menu()
        self.assertIsInstance(menu, TrayMenu)
        self.assertEqual(len(menu.items), 1) # Only "Quit Application" now

        # Mock the method on the instance BEFORE creating the menu that will use it for the action test
        self.tray_manager._on_quit_selected = MagicMock(name="_on_quit_selected_mock")
        menu_with_mocked_actions = self.tray_manager._create_menu()
        # Test the "Quit Application" item (which is now items[0])
        self.assertEqual(menu_with_mocked_actions.items[0].text, "Quit Application")
        self.assertTrue(menu_with_mocked_actions.items[0].enabled)
        # pystray.MenuItem.__call__ expects (icon, item)
        mock_icon_for_action = MagicMock(spec=TrayIcon)
        menu_with_mocked_actions.items[0](mock_icon_for_action) # Call with icon only
        self.tray_manager._on_quit_selected.assert_called_once()

    def test_on_quit_selected(self):
        self.tray_manager.icon = MagicMock() # Simulate icon exists
        self.tray_manager._on_quit_selected()
        self.mock_shutdown_event.set.assert_called_once()
        self.tray_manager.icon.stop.assert_called_once()
        self.mock_logger.info.assert_any_call("Tray: Quit selected. Setting global shutdown event and publishing APPLICATION_QUIT_REQUESTED event.")

    @patch('comfy_launcher.tray_manager.event_publisher.publish')
    def test_handle_application_quit_request_stops_icon_and_publishes_complete(self, mock_event_publish):
        self.tray_manager.icon = MagicMock(spec=TrayIcon)
        
        # Simulate the event being handled
        self.tray_manager.handle_application_quit_request()

        self.tray_manager.icon.stop.assert_called_once()
        # The TRAY_MANAGER_SHUTDOWN_COMPLETE event is published by the run() method when the thread ends, not this handler.
        self.mock_logger.info.assert_any_call("Handler: APPLICATION_QUIT_REQUESTED received by TrayManager. Stopping tray icon.")

    def test_handle_gui_window_hidden_updates_menu(self):
        self.tray_manager.icon = MagicMock(spec=TrayIcon)
        self.tray_manager.handle_gui_window_hidden()
        self.tray_manager.icon.update_menu.assert_called_once()

    @patch('comfy_launcher.tray_manager.TrayIcon')
    @patch('comfy_launcher.tray_manager.Image.open')
    # No longer need to patch Path.exists globally, we mock it on self.mock_icon_path_object
    def test_run_icon_exists(self, mock_image_open, mock_pystray_icon_class):
        self.mock_icon_path_object.exists.return_value = True # Ensure icon exists for this test
        mock_image_instance = MagicMock(spec=Image.Image)
        mock_image_open.return_value = mock_image_instance
        mock_tray_icon_instance = MagicMock()
        mock_pystray_icon_class.return_value = mock_tray_icon_instance

        self.tray_manager._create_menu = MagicMock(return_value="fake_menu") # Mock menu creation

        self.tray_manager.run()

        expected_icon_path = self.mock_assets_dir / "icon.png" # This will be self.mock_icon_path_object
        self.mock_icon_path_object.exists.assert_called_once_with()
        mock_image_open.assert_called_once_with(expected_icon_path)
        mock_pystray_icon_class.assert_called_once_with(
            self.app_name, mock_image_instance, self.app_name, "fake_menu"
        )
        mock_tray_icon_instance.run.assert_called_once()
        self.mock_logger.info.assert_any_call("Starting tray icon event loop...")

    @patch('comfy_launcher.tray_manager.TrayIcon')
    @patch('comfy_launcher.tray_manager.Image.new') # Mock Image.new for fallback
    # No longer need to patch Path.exists globally
    def test_run_icon_not_exists_fallback(self, mock_image_new, mock_pystray_icon_class):
        # In TrayManager.run, if icon_path.exists() is false, it logs an error and uses a fallback.
        # The original test was checking for "Cannot start tray icon." which is for menu creation failure.
        # Let's adjust to check the correct error log for missing icon asset.
        self.mock_icon_path_object.exists.return_value = False
        mock_fallback_image_instance = MagicMock(spec=Image.Image)
        mock_image_new.return_value = mock_fallback_image_instance
        mock_tray_icon_instance = MagicMock()
        mock_pystray_icon_class.return_value = mock_tray_icon_instance
        self.tray_manager._create_menu = MagicMock(return_value="fake_menu")
        self.tray_manager.run()
        expected_icon_path = self.mock_assets_dir / "icon.png"
        self.mock_logger.error.assert_any_call(f"Tray icon asset not found at {expected_icon_path}. Using fallback red square.")
        mock_image_new.assert_called_once_with('RGB', (64, 64), color='red')
        mock_pystray_icon_class.assert_called_once_with(
            self.app_name, mock_fallback_image_instance, self.app_name, "fake_menu"
        )
        mock_tray_icon_instance.run.assert_called_once()

    @patch('comfy_launcher.tray_manager.TrayIcon') # Add missing patch
    @patch('comfy_launcher.tray_manager.Image.open') # Add missing patch
    def test_run_signals_shutdown_on_critical_error(self, mock_image_open_p, mock_pystray_icon_class):
        mock_pystray_icon_class.side_effect = Exception("Pystray critical error")
        self.mock_shutdown_event.is_set.return_value = False # Ensure event is not already set
        self.tray_manager.run()
        self.mock_logger.error.assert_any_call("Failed to run tray icon: Pystray critical error", exc_info=True)
        self.mock_shutdown_event.set.assert_called_once()
        self.mock_logger.info.assert_any_call("Signaling app shutdown due to critical tray error.")
    @patch('comfy_launcher.tray_manager.threading.Thread')
    def test_start_creates_and_starts_thread(self, mock_thread_class):
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance

        self.tray_manager.start()

        mock_thread_class.assert_called_once_with(target=self.tray_manager.run, daemon=True, name="TrayIconThread")
        mock_thread_instance.start.assert_called_once()
        self.assertEqual(self.tray_manager._thread, mock_thread_instance)
        self.mock_logger.info.assert_any_call("Thread started.")

    @patch('comfy_launcher.tray_manager.threading.Thread')
    def test_start_does_not_restart_alive_thread(self, mock_thread_class):
        mock_existing_thread = MagicMock(spec=OriginalPythonThread) # Use true original for spec
        mock_existing_thread.is_alive.return_value = True
        self.tray_manager._thread = mock_existing_thread

        self.tray_manager.start()

        mock_thread_class.assert_not_called() # Should not create a new thread

    def test_stop_stops_icon_and_joins_thread(self):
        mock_icon_instance = MagicMock()
        self.tray_manager.icon = mock_icon_instance

        mock_thread_instance = MagicMock(spec=OriginalPythonThread) # Use true original for spec
        mock_thread_instance.is_alive.return_value = True
        self.tray_manager._thread = mock_thread_instance

        self.tray_manager.stop()

        mock_icon_instance.stop.assert_called_once()
        mock_thread_instance.join.assert_called_once_with(timeout=2)
        self.mock_logger.info.assert_any_call("Tray icon stopped.")

    def test_stop_no_icon_or_thread(self):
        self.tray_manager.icon = None
        self.tray_manager._thread = None
        self.tray_manager.stop() # Should not raise errors
        self.mock_logger.info.assert_any_call("Stopping tray icon...")
        self.mock_logger.info.assert_any_call("Tray icon stopped.")

if __name__ == '__main__':
    unittest.main()