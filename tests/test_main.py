import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import threading # Keep for spec
import logging
import subprocess # For spec in app_logic_thread_func test

import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher import __main__ as launcher_main_module
from comfy_launcher.gui_manager import GUIManager
from comfy_launcher.server_manager import ServerManager
from comfy_launcher.tray_manager import TrayManager # For spec
# Import the function we need to test directly if it's not too complex to call
from comfy_launcher.__main__ import app_logic_thread_func


@patch('comfy_launcher.__main__.TrayManager')
class TestMainExecution(unittest.TestCase):


    @patch('comfy_launcher.__main__.app_logic_thread_func') # Patch the function directly
    @patch('comfy_launcher.__main__.time.sleep', return_value=None) # Keep if app_logic_thread_func uses it
    @patch('comfy_launcher.__main__.GUIManager')
    @patch('comfy_launcher.__main__.ServerManager')
    @patch('comfy_launcher.__main__.rotate_and_cleanup_logs')
    @patch('comfy_launcher.__main__.setup_launcher_logger')
    @patch('comfy_launcher.__main__.settings')
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=threading.Event))
    def test_main_orchestration_and_shutdown( # Order: innermost @patch first, then class @patch
            self, mock_app_shutdown_event_p,    # from @patch('...app_shutdown_event')
            mock_settings_p,                # from @patch('...settings')
            mock_setup_logger_p,            # from @patch('...setup_launcher_logger')
            mock_rotate_cleanup_p,          # from @patch('...rotate_and_cleanup_logs')
            MockServerManager_p,            # from @patch('...ServerManager')
            MockGUIManager_p,               # from @patch('...GUIManager')
            mock_time_sleep_p,              # from @patch('...time.sleep')
            mock_app_logic_thread_func_p,   # from @patch('...app_logic_thread_func')
            MockTrayManager_class_level_p ):# From class decorator
        """
        Test the main orchestration flow: setup, GUI prep, thread start, webview start, and shutdown.
        The internal logic of app_logic_thread_func is tested separately.
        """
        mock_logger_instance = MagicMock(spec=logging.Logger)
        mock_setup_logger_p.return_value = mock_logger_instance

        mock_gui_instance = MockGUIManager_p.return_value
        mock_server_instance = MockServerManager_p.return_value
        mock_tray_instance = MockTrayManager_class_level_p.return_value

        # Simulate app_shutdown_event.wait() being unblocked by app_shutdown_event.set()
        # This is a simplified way; a more complex side_effect could be used if needed.
        def shutdown_side_effect():
            mock_app_shutdown_event_p.set() # Simulate something setting the event
        mock_gui_instance.start_webview_blocking.side_effect = shutdown_side_effect

        # Configure settings
        mock_settings_p.DEBUG = False
        mock_settings_p.APP_NAME = "TestApp"
        mock_settings_p.LOG_DIR = Path("/fake/logs")
        mock_settings_p.MAX_LOG_FILES = 3
        mock_settings_p.MAX_LOG_AGE_DAYS = 5
        mock_settings_p.COMFYUI_PATH = Path("/fake/comfyui")
        mock_settings_p.PYTHON_EXECUTABLE = Path("/fake/python")
        mock_settings_p.HOST = "127.0.0.1"
        mock_settings_p.PORT = 8188
        mock_settings_p.ASSETS_DIR = Path("/fake/assets")
        mock_settings_p.WINDOW_WIDTH = 800
        mock_settings_p.WINDOW_HEIGHT = 600
        mock_settings_p.EFFECTIVE_CONNECT_HOST = mock_settings_p.HOST

        # --- Simulate main execution ---
        # Patch threading.Thread to capture its arguments and control its behavior
        with patch('comfy_launcher.__main__.threading.Thread') as MockAppThread:
            mock_thread_instance = MockAppThread.return_value
            launcher_main_module.main()

            # 1. Initial setup assertions
            mock_rotate_cleanup_p.assert_called_once_with(
                mock_settings_p.LOG_DIR, mock_settings_p.MAX_LOG_FILES, mock_settings_p.MAX_LOG_AGE_DAYS
            )
            mock_setup_logger_p.assert_called_once_with(
                mock_settings_p.LOG_DIR, mock_settings_p.DEBUG
            )

            # 2. Manager instantiation
            MockServerManager_p.assert_called_once_with(
                comfyui_path=mock_settings_p.COMFYUI_PATH,
                python_executable=mock_settings_p.PYTHON_EXECUTABLE,
                listen_host=mock_settings_p.HOST,
                connect_host=mock_settings_p.EFFECTIVE_CONNECT_HOST,
                port=mock_settings_p.PORT,
                logger=mock_logger_instance
            )
            MockGUIManager_p.assert_called_once_with(
                app_name=mock_settings_p.APP_NAME,
                window_width=mock_settings_p.WINDOW_WIDTH,
                window_height=mock_settings_p.WINDOW_HEIGHT,
                connect_host=mock_settings_p.EFFECTIVE_CONNECT_HOST,
                port=mock_settings_p.PORT,
                assets_dir=mock_settings_p.ASSETS_DIR,
                logger=mock_logger_instance,
                server_manager=mock_server_instance
            )
            MockTrayManager_class_level_p.assert_called_once_with(
                app_name=mock_settings_p.APP_NAME,
                assets_dir=mock_settings_p.ASSETS_DIR,
                logger=mock_logger_instance,
                shutdown_event=mock_app_shutdown_event_p, # Check new arg
                gui_manager=mock_gui_instance          # Check new arg
            )

            # 3. GUI preparation
            mock_gui_instance.prepare_and_launch_gui.assert_called_once_with(
                shutdown_event_for_critical_error=mock_app_shutdown_event_p # Check new arg
            )

            # 3.5 Tray Manager start
            mock_tray_instance.start.assert_called_once()

            # 4. Assert app_logic_thread was created and started correctly
            expected_server_log_path = mock_settings_p.LOG_DIR / "server.log"
            MockAppThread.assert_called_once_with(
                target=launcher_main_module.app_logic_thread_func, # Check it's the right function
                args=(mock_logger_instance, mock_gui_instance, mock_server_instance,
                      expected_server_log_path, mock_app_shutdown_event_p), # Check new arg
                daemon=True
            )
            mock_thread_instance.start.assert_called_once()

            # 5. Webview blocking start
            mock_gui_instance.start_webview_blocking.assert_called_once()
            
            # 5.5 Assert app_shutdown_event.wait() was called
            mock_app_shutdown_event_p.wait.assert_called_once()

            # 6. Shutdown sequence (after webview_blocking returns)
            mock_app_shutdown_event_p.set.assert_called() # Ensure it was set to unblock wait

            self.assertEqual(launcher_main_module.server_manager_instance, mock_server_instance)
            self.assertEqual(launcher_main_module.tray_manager_instance, mock_tray_instance)

            # Server shutdown is now primarily in app_logic_thread_func, but main does a final check
            # If server_process is None or already polled, shutdown_server won't be called from main's finally
            # This assertion might need to be more nuanced or removed if app_logic_thread handles it all.
            # For now, let's assume it might be called if the process is still seen as running.
            # mock_server_instance.shutdown_server.assert_called_once_with()

            mock_tray_instance.stop.assert_called_once_with() # Check tray stop
            mock_gui_instance.webview_window.destroy.assert_called_once() # Check GUI destroy

            # 7. Final logging
            mock_logger_instance.info.assert_any_call(f"MAIN THREAD: {mock_settings_p.APP_NAME} has exited cleanly.")
            # 8. Thread join
            mock_thread_instance.join.assert_called_once_with(timeout=10)


    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread')
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=threading.Event))
    def test_app_logic_thread_func_successful_run(self, mock_app_shutdown_event_p, # from @patch('...app_shutdown_event')
                                                mock_threading_Thread_p,      # from @patch('...threading.Thread')
                                                mock_time_sleep_p,            # from @patch('...time.sleep')
                                                MockTrayManager_class_level_param): # From class decorator
        """
        Test the successful execution flow of app_logic_thread_func.
        """
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_app_shutdown_event_p # Use the one from the decorator

        # Simulate GUI loaded successfully
        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = True

        mock_shutdown_event.is_set.return_value = False # Ensure initial checks pass
        # Simulate server starting successfully
        mock_server_process_obj = MagicMock(spec=subprocess.Popen, pid=12345)
        mock_server_process_obj.poll.return_value = None # Crucial: Simulate server is running initially
        mock_server_manager.start_server.return_value = mock_server_process_obj
        # Simulate server running and then shutdown_event being set
        # More explicit side_effect for mock_shutdown_event.wait based on call order
        _wait_call_count = 0
        def shutdown_wait_side_effect(timeout):
            nonlocal _wait_call_count
            _wait_call_count += 1
            if _wait_call_count == 1: # First call, should be wait(0.5)
                self.assertEqual(timeout, 0.5, "First wait call should be 0.5s")
                return False
            elif _wait_call_count == 2: # Second call, should be wait(0.5)
                self.assertEqual(timeout, 0.5, "Second wait call should be 0.5s")
                return False
            elif _wait_call_count == 3: # Third call, should be wait(timeout=1) in monitoring loop
                self.assertEqual(timeout, 1, "Third wait call should be 1s timeout")
                # Do NOT change poll.return_value here.
                # Let the poll() in the finally block see the server as still running (None).
                return True # Simulate event was set
            # Should not be reached if logic is correct for this test
            raise AssertionError(f"Unexpected call to shutdown_event.wait with timeout={timeout} at call_count={_wait_call_count}")
        mock_shutdown_event.wait.side_effect = shutdown_wait_side_effect


        # Simulate settings for port
        with patch('comfy_launcher.__main__.settings') as mock_main_settings:
            mock_main_settings.PORT = 8188
            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                                  mock_server_log_path, mock_shutdown_event)

        # Assertions for app_logic_thread_func
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Started.")
        mock_gui_manager.is_window_loaded.wait.assert_called_once_with(timeout=20)
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Waiting for GUI window to finish loading content...")
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: GUI content loaded. Proceeding with server launch sequence.")

        mock_gui_manager.set_status.assert_any_call("Initializing...")
        mock_shutdown_event.wait.assert_any_call(0.5) # Check for waits

        mock_gui_manager.set_status.assert_any_call(f"Clearing network port {mock_main_settings.PORT}...")
        mock_server_manager.kill_process_on_port.assert_called_once()

        mock_gui_manager.set_status.assert_any_call("Starting ComfyUI server process...")
        mock_server_manager.start_server.assert_called_once_with(mock_server_log_path)

        # Assert the redirect_when_ready_loop thread was started
        mock_redirect_stop_event_arg = mock_threading_Thread_p.call_args[1]['args'][0]
        self.assertIsInstance(mock_redirect_stop_event_arg, threading.Event)

        mock_threading_Thread_p.assert_called_once_with(
            target=mock_gui_manager.redirect_when_ready_loop,
            args=(mock_redirect_stop_event_arg, mock_shutdown_event), # Check new args
            daemon=True
        )
        mock_threading_Thread_p.return_value.start.assert_called_once()
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Redirection loop initiated.")

        # Assert server monitoring loop
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Now monitoring server process and shutdown event.")
        mock_server_process_obj.poll.assert_called()
        mock_shutdown_event.wait.assert_any_call(timeout=1)

        # Assert cleanup
        mock_app_logger.info.assert_any_call("BACKGROUND THREAD: Cleaning up...")
        self.assertTrue(mock_redirect_stop_event_arg.is_set()) # Check redirect stop event was set
        mock_server_manager.shutdown_server.assert_called_once() # Server shutdown in finally

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=threading.Event))
    def test_app_logic_thread_func_gui_timeout(self, mock_app_shutdown_event_p, # from @patch('...app_shutdown_event')
                                               mock_time_sleep_p,            # from @patch('...time.sleep')
                                               MockTrayManager_class_level_param): # From class decorator
        """Test app_logic_thread_func when GUI fails to load."""
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager) # Not used much here
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_app_shutdown_event_p

        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = False # Simulate timeout
        mock_gui_manager.webview_window = MagicMock() # So it can try to load_html
        # mock_gui_manager._get_asset_content.return_value = "Critical Error HTML {MESSAGE}" # No longer needed here
        mock_shutdown_event.is_set.return_value = False # Simulate not already shutting down

        app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                              mock_server_log_path, mock_shutdown_event)

        mock_app_logger.error.assert_any_call("BACKGROUND THREAD: GUI window did not signal 'loaded' in time. Aborting app logic.")
        # Assert that load_critical_error_page is called, not its internal _get_asset_content
        mock_gui_manager.load_critical_error_page.assert_called_once_with("GUI did not load correctly. Check launcher logs.")
        mock_server_manager.kill_process_on_port.assert_not_called() # Should not proceed this far
        mock_shutdown_event.set.assert_called_once() # Should signal shutdown

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread') # For redirect thread
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=threading.Event))
    def test_app_logic_thread_func_server_start_fails(self, mock_app_shutdown_event_p, # from @patch('...app_shutdown_event')
                                                      mock_threading_Thread_p,      # from @patch('...threading.Thread')
                                                      mock_time_sleep_p,            # from @patch('...time.sleep')
                                                      MockTrayManager_class_level_param): # From class decorator
        """Test app_logic_thread_func when server fails to start."""
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_app_shutdown_event_p

        mock_gui_manager.is_window_loaded = MagicMock(spec=threading.Event)
        mock_gui_manager.is_window_loaded.wait.return_value = True
        mock_server_manager.start_server.return_value = None # Simulate server start failure
        mock_gui_manager.webview_window = MagicMock()
        # mock_gui_manager._get_asset_content.return_value = "Error HTML {ERROR_MESSAGE}" # No longer needed here
        mock_shutdown_event.is_set.return_value = False # Simulate not already shutting down
        # Ensure initial waits don't cause early exit
        initial_wait_return_values = [False, False, False]
        def temp_wait_side_effect(timeout):
            if initial_wait_return_values: return initial_wait_return_values.pop(0)
            return False
        mock_shutdown_event.wait.side_effect = temp_wait_side_effect

        with patch('comfy_launcher.__main__.settings') as mock_main_settings:
            mock_main_settings.PORT = 8188
            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                                  mock_server_log_path, mock_shutdown_event)

        mock_app_logger.error.assert_any_call("BACKGROUND THREAD: Failed to start ComfyUI server process. Aborting app logic.")
        mock_gui_manager.load_error_page.assert_called_once_with("Could not start the ComfyUI server. Please check the server.log file for details.")
        mock_threading_Thread_p.assert_not_called() # Redirect loop should not start
        mock_shutdown_event.set.assert_called_once() # Should signal shutdown

if __name__ == '__main__':
    unittest.main()
