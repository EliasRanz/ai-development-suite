import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import threading
import logging
import subprocess # For spec in app_logic_thread_func test

import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher import __main__ as launcher_main_module
from comfy_launcher.gui_manager import GUIManager
from comfy_launcher.server_manager import ServerManager
# Import the function we need to test directly if it's not too complex to call
from comfy_launcher.__main__ import app_logic_thread_func


class TestMainExecution(unittest.TestCase):

    @patch('comfy_launcher.__main__.app_logic_thread_func') # Patch the function directly
    @patch('comfy_launcher.__main__.time.sleep', return_value=None) # Keep if app_logic_thread_func uses it
    @patch('comfy_launcher.__main__.GUIManager')
    @patch('comfy_launcher.__main__.ServerManager')
    @patch('comfy_launcher.__main__.rotate_and_cleanup_logs')
    @patch('comfy_launcher.__main__.setup_launcher_logger')
    @patch('comfy_launcher.__main__.settings')
    def test_main_orchestration_and_shutdown(
            self, mock_settings, mock_setup_logger, mock_rotate_cleanup,
            MockServerManager, MockGUIManager,
            mock_time_sleep, # Keep if used by main or app_logic_thread_func
            mock_app_logic_thread_func_target): # Renamed for clarity
        """
        Test the main orchestration flow: setup, GUI prep, thread start, webview start, and shutdown.
        The internal logic of app_logic_thread_func is tested separately.
        """
        mock_logger_instance = MagicMock(spec=logging.Logger)
        mock_setup_logger.return_value = mock_logger_instance

        mock_gui_instance = MockGUIManager.return_value
        mock_server_instance = MockServerManager.return_value

        # Configure settings
        mock_settings.DEBUG = False
        mock_settings.APP_NAME = "TestApp"
        mock_settings.LOG_DIR = Path("/fake/logs")
        mock_settings.MAX_LOG_FILES = 3
        mock_settings.MAX_LOG_AGE_DAYS = 5
        mock_settings.COMFYUI_PATH = Path("/fake/comfyui")
        mock_settings.PYTHON_EXECUTABLE = Path("/fake/python")
        mock_settings.HOST = "127.0.0.1"
        mock_settings.PORT = 8188
        mock_settings.ASSETS_DIR = Path("/fake/assets")
        mock_settings.WINDOW_WIDTH = 800
        mock_settings.WINDOW_HEIGHT = 600
        mock_settings.EFFECTIVE_CONNECT_HOST = mock_settings.HOST

        # --- Simulate main execution ---
        # Patch threading.Thread to capture its arguments and control its behavior
        with patch('comfy_launcher.__main__.threading.Thread') as MockAppThread:
            mock_thread_instance = MockAppThread.return_value

            launcher_main_module.main()

            # 1. Initial setup assertions
            mock_rotate_cleanup.assert_called_once_with(
                mock_settings.LOG_DIR, mock_settings.MAX_LOG_FILES, mock_settings.MAX_LOG_AGE_DAYS
            )
            mock_setup_logger.assert_called_once_with(
                mock_settings.LOG_DIR, mock_settings.DEBUG
            )

            # 2. Manager instantiation
            MockServerManager.assert_called_once_with(
                comfyui_path=mock_settings.COMFYUI_PATH,
                python_executable=mock_settings.PYTHON_EXECUTABLE,
                listen_host=mock_settings.HOST,
                connect_host=mock_settings.EFFECTIVE_CONNECT_HOST,
                port=mock_settings.PORT,
                logger=mock_logger_instance
            )
            MockGUIManager.assert_called_once_with(
                app_name=mock_settings.APP_NAME,
                window_width=mock_settings.WINDOW_WIDTH,
                window_height=mock_settings.WINDOW_HEIGHT,
                connect_host=mock_settings.EFFECTIVE_CONNECT_HOST,
                port=mock_settings.PORT,
                assets_dir=mock_settings.ASSETS_DIR,
                logger=mock_logger_instance,
                server_manager=mock_server_instance
            )

            # 3. GUI preparation
            mock_gui_instance.prepare_and_launch_gui.assert_called_once()

            # 4. Assert app_logic_thread was created and started correctly
            expected_server_log_path = mock_settings.LOG_DIR / "server.log"
            MockAppThread.assert_called_once_with(
                target=launcher_main_module.app_logic_thread_func, # Check it's the right function
                args=(mock_logger_instance, mock_gui_instance, mock_server_instance, expected_server_log_path),
                daemon=True
            )
            mock_thread_instance.start.assert_called_once()

            # 5. Webview blocking start
            mock_gui_instance.start_webview_blocking.assert_called_once()

            # 6. Shutdown sequence (after webview_blocking returns)
            # Ensure server_manager_instance was set correctly in main
            self.assertEqual(launcher_main_module.server_manager_instance, mock_server_instance)
            mock_server_instance.shutdown_server.assert_called_once_with() # No arguments now

            # 7. Final logging
            mock_logger_instance.info.assert_any_call(f"MAIN THREAD: {mock_settings.APP_NAME} has exited cleanly.")

            # 8. Thread join
            mock_thread_instance.join.assert_called_once_with(timeout=5)


    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread') # For the redirect_when_ready_loop thread
    def test_app_logic_thread_func_successful_run(self, mock_redirect_thread_class, mock_time_sleep_ignored):
        """
        Test the successful execution flow of app_logic_thread_func.
        """
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")

        # Simulate GUI loaded successfully
        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = True

        # Simulate server starting successfully
        mock_server_process_obj = MagicMock(spec=subprocess.Popen, pid=12345)
        mock_server_manager.start_server.return_value = mock_server_process_obj

        # Simulate settings for port
        with patch('comfy_launcher.__main__.settings') as mock_main_settings:
            mock_main_settings.PORT = 8188

            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager, mock_server_log_path)

        # Assertions for app_logic_thread_func
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Started.")
        mock_gui_manager.is_window_loaded.wait.assert_called_once_with(timeout=20)
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: GUI content loaded. Proceeding with server launch sequence.")

        mock_gui_manager.set_status.assert_any_call("Initializing...")
        # time.sleep(0.5) - mock_time_sleep handles this

        mock_gui_manager.set_status.assert_any_call(f"Clearing network port {mock_main_settings.PORT}...")
        mock_server_manager.kill_process_on_port.assert_called_once()
        # time.sleep(0.5)

        mock_gui_manager.set_status.assert_any_call("Starting ComfyUI server process...")
        mock_server_manager.start_server.assert_called_once_with(mock_server_log_path)

        # Assert the redirect_when_ready_loop thread was started
        mock_redirect_thread_class.assert_called_once_with(
            target=mock_gui_manager.redirect_when_ready_loop, daemon=True
        )
        mock_redirect_thread_class.return_value.start.assert_called_once()
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Redirection loop initiated.")
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Finished its primary tasks.")

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    def test_app_logic_thread_func_gui_timeout(self, mock_time_sleep_ignored):
        """Test app_logic_thread_func when GUI fails to load."""
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager) # Not used much here
        mock_server_log_path = Path("/fake/logs/server.log")

        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = False # Simulate timeout
        mock_gui_manager.webview_window = MagicMock() # So it can try to load_html
        mock_gui_manager._get_asset_content.return_value = "Critical Error HTML {MESSAGE}"

        app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager, mock_server_log_path)

        mock_app_logger.error.assert_any_call("BACKGROUND THREAD: GUI window did not signal 'loaded' in time. Aborting app logic.")
        mock_gui_manager._get_asset_content.assert_called_once_with("critical_error.html", is_critical_fallback=True)
        mock_gui_manager.webview_window.load_html.assert_called_once_with("Critical Error HTML GUI did not load correctly. Check launcher logs.")
        mock_server_manager.kill_process_on_port.assert_not_called() # Should not proceed this far

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread') # For redirect thread
    def test_app_logic_thread_func_server_start_fails(self, mock_redirect_thread_class, mock_time_sleep_ignored):
        """Test app_logic_thread_func when server fails to start."""
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")

        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = True
        mock_server_manager.start_server.return_value = None # Simulate server start failure
        mock_gui_manager.webview_window = MagicMock()
        mock_gui_manager._get_asset_content.return_value = "Error HTML {ERROR_MESSAGE}"

        with patch('comfy_launcher.__main__.settings') as mock_main_settings:
            mock_main_settings.PORT = 8188
            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager, mock_server_log_path)

        mock_app_logger.error.assert_any_call("BACKGROUND THREAD: Failed to start ComfyUI server process. Aborting app logic.")
        mock_gui_manager._get_asset_content.assert_called_once_with("error.html", is_critical_fallback=True)
        mock_gui_manager.webview_window.load_html.assert_called_once_with("Error HTML Could not start the ComfyUI server. Please check the server.log file for details.")
        mock_redirect_thread_class.assert_not_called() # Redirect loop should not start

if __name__ == '__main__':
    unittest.main()
