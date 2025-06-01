import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import threading as python_threading # Alias for actual threading module to avoid patch conflicts
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
# Import functions and event handlers we need to test directly
from comfy_launcher.__main__ import app_logic_thread_func


@patch('comfy_launcher.__main__.TrayManager')
class TestMainExecution(unittest.TestCase):
    # Store the original Event class before any patches
    OriginalEventClass = python_threading.Event


    @patch('comfy_launcher.__main__.app_logic_thread_func') # Patch the function directly
    @patch('comfy_launcher.__main__.time.sleep', return_value=None) # Keep if app_logic_thread_func uses it
    @patch('comfy_launcher.__main__.GUIManager')
    @patch('comfy_launcher.__main__.ServerManager')
    @patch('comfy_launcher.__main__.LogManager')
    @patch('comfy_launcher.__main__.settings')
    # Patch global event instances, speccing against the original Event class
    @patch('comfy_launcher.__main__._app_logic_completed_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    @patch('comfy_launcher.__main__._tray_manager_completed_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    # Patch the Event class within __main__'s threading module, also speccing against the original
    @patch('comfy_launcher.__main__.threading.Event', new_callable=lambda: unittest.mock.create_autospec(TestMainExecution.OriginalEventClass, instance=False))
    def test_main_orchestration_and_shutdown(
            self,
            mock_sut_local_event_constructor_p, # from @patch('...threading.Event')
            mock_app_shutdown_event_p,          # from @patch('...app_shutdown_event')
            mock_tray_manager_completed_event_global_p, # from @patch('..._tray_manager_completed_event')
            mock_app_logic_completed_event_global_p,    # from @patch('..._app_logic_completed_event')
            mock_settings_p,
            MockLogManager_p,
            MockServerManager_p,
            MockGUIManager_p,
            mock_time_sleep_p,
            mock_app_logic_thread_func_p,
            MockTrayManager_class_level_p): # From class decorator
        """
        Test the main orchestration flow: LogManager init, GUI prep, thread start, webview start, and shutdown.
        The internal logic of app_logic_thread_func is tested separately.
        """
        mock_log_manager_instance = MockLogManager_p.return_value
        mock_logger_instance = MagicMock(spec=logging.Logger, name="MockLoggerInstance")
        mock_log_manager_instance.get_launcher_logger.return_value = mock_logger_instance

        mock_gui_instance = MockGUIManager_p.return_value
        mock_server_instance = MockServerManager_p.return_value
        mock_tray_instance = MockTrayManager_class_level_p.return_value

        # _app_logic_completed_event and _tray_manager_completed_event are now global and patched directly.
        # mock_sut_local_event_constructor_p will catch any *other* threading.Event() calls within main.py if they exist.
        # No need for: mock_sut_event_constructor_p.side_effect = [...]

        # Simulate app_shutdown_event.wait() being unblocked by app_shutdown_event.set()
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
        with patch('comfy_launcher.__main__.threading.Thread') as MockAppThread:
            mock_thread_instance = MockAppThread.return_value
            launcher_main_module.main()

            # 1. Initial setup assertions
            MockLogManager_p.assert_called_once_with(
                log_dir=mock_settings_p.LOG_DIR,
                debug_mode=mock_settings_p.DEBUG,
                max_files_to_keep_in_archive=mock_settings_p.MAX_LOG_FILES,
                max_log_age_days=mock_settings_p.MAX_LOG_AGE_DAYS
            )
            mock_log_manager_instance.get_launcher_logger.assert_called_once()

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
                shutdown_event=mock_app_shutdown_event_p,
                gui_manager=mock_gui_instance
            )

            # 3. GUI preparation
            mock_gui_instance.prepare_and_launch_gui.assert_called_once_with(
                shutdown_event_for_critical_error=mock_app_shutdown_event_p
            )

            # 3.5 Tray Manager start
            mock_tray_instance.start.assert_called_once()

            # 4. Assert app_logic_thread was created and started correctly
            expected_server_log_path = mock_settings_p.LOG_DIR / "server.log"
            MockAppThread.assert_called_once_with(
                target=launcher_main_module.app_logic_thread_func,
                args=(mock_logger_instance, mock_gui_instance, mock_server_instance,
                      expected_server_log_path, mock_app_shutdown_event_p),
                daemon=True
            )
            mock_thread_instance.start.assert_called_once()

            # 5. Webview blocking start
            mock_gui_instance.start_webview_blocking.assert_called_once()
            
            # 5.5 Assert app_shutdown_event.wait() was called
            mock_app_shutdown_event_p.wait.assert_called_once()

            # 6. Shutdown sequence
            mock_app_shutdown_event_p.set.assert_called()

            self.assertEqual(launcher_main_module.server_manager_instance, mock_server_instance)
            self.assertEqual(launcher_main_module.tray_manager_instance, mock_tray_instance)

            if mock_gui_instance.webview_window:
                mock_gui_instance.webview_window.destroy.assert_called_once()

            # 7. Final logging
            mock_logger_instance.info.assert_any_call(f"{mock_settings_p.APP_NAME} has exited cleanly.")
            mock_app_logic_completed_event_global_p.wait.assert_called_once_with(timeout=12)
            mock_tray_manager_completed_event_global_p.wait.assert_called_once_with(timeout=5)

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread')
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    def test_app_logic_thread_func_successful_run(self, mock_app_shutdown_event_p,
                                                mock_threading_Thread_p,
                                                mock_time_sleep_p,
                                                MockTrayManager_class_level_param):
        """
        Test the successful execution flow of app_logic_thread_func.
        """
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_app_shutdown_event_p

        mock_event_publisher = MagicMock()
        _gui_initial_content_loaded_event_for_test = self.OriginalEventClass()

        mock_shutdown_event.is_set.return_value = False
        mock_server_process_obj = MagicMock(spec=subprocess.Popen, pid=12345)
        mock_server_process_obj.poll.return_value = None
        mock_server_manager.start_server.return_value = mock_server_process_obj
        
        _wait_call_count = 0
        def shutdown_wait_side_effect(timeout):
            nonlocal _wait_call_count
            _wait_call_count += 1
            if _wait_call_count == 1:
                self.assertEqual(timeout, 0.5, "First wait call should be 0.5s")
                return False
            elif _wait_call_count == 2:
                self.assertEqual(timeout, 0.5, "Second wait call should be 0.5s")
                return False
            elif _wait_call_count == 3:
                self.assertEqual(timeout, 1, "Third wait call should be 1s timeout")
                return True
            raise AssertionError(f"Unexpected call to shutdown_event.wait with timeout={timeout} at call_count={_wait_call_count}")
        mock_shutdown_event.wait.side_effect = shutdown_wait_side_effect

        with patch('comfy_launcher.__main__.settings') as mock_main_settings, \
             patch('comfy_launcher.__main__.event_publisher', mock_event_publisher), \
             patch('comfy_launcher.__main__.threading.Event', MagicMock(return_value=_gui_initial_content_loaded_event_for_test)):
            
            mock_main_settings.PORT = 8188
            _gui_initial_content_loaded_event_for_test.set()

            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                                  mock_server_log_path, mock_shutdown_event)

        mock_app_logger.info.assert_any_call("Started.")
        self.assertTrue(_gui_initial_content_loaded_event_for_test.is_set())
        mock_app_logger.info.assert_any_call("Waiting for GUI window to finish loading initial content (via event)...")
        mock_app_logger.info.assert_any_call("GUI content loaded. Proceeding with server launch sequence.")

        mock_gui_manager.set_status.assert_any_call("Initializing...")
        mock_shutdown_event.wait.assert_any_call(0.5)

        mock_gui_manager.set_status.assert_any_call(f"Clearing network port {mock_main_settings.PORT}...")
        mock_server_manager.kill_process_on_port.assert_called_once()
        mock_gui_manager.set_status.assert_any_call("Starting ComfyUI server process...")
        mock_server_manager.start_server.assert_called_once_with(mock_server_log_path)

        if mock_threading_Thread_p.called:
            mock_redirect_stop_event_arg = mock_threading_Thread_p.call_args[1]['args'][0]
            self.assertIsInstance(mock_redirect_stop_event_arg, python_threading.Event)

            mock_threading_Thread_p.assert_called_once_with(
                target=mock_gui_manager.redirect_when_ready_loop,
                args=(mock_redirect_stop_event_arg, mock_shutdown_event),
                daemon=True
            )
            mock_threading_Thread_p.return_value.start.assert_called_once()
        else:
            self.fail("threading.Thread for redirect_when_ready_loop was not called.")
        mock_app_logger.info.assert_any_call("Redirection loop initiated.")

        mock_app_logger.info.assert_any_call("Now monitoring server process and shutdown event.")
        mock_server_process_obj.poll.assert_called()
        mock_shutdown_event.wait.assert_any_call(timeout=1)

        mock_app_logger.info.assert_any_call("Cleaning up...")
        self.assertTrue(mock_redirect_stop_event_arg.is_set())
        mock_server_manager.shutdown_server.assert_called_once()

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    @patch('comfy_launcher.__main__.threading.Event')
    def test_app_logic_thread_func_gui_timeout(self, mock_sut_event_constructor,
                                               mock_global_app_shutdown_event,
                                               mock_time_sleep,
                                               MockTrayManager_class_level_param):
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_global_app_shutdown_event

        mock_event_publisher = MagicMock()
        mock_gui_load_event_instance_for_timeout = MagicMock(spec=self.OriginalEventClass, name="MockGuiLoadEventForTimeout")
        mock_gui_load_event_instance_for_timeout.wait.return_value = False
        mock_sut_event_constructor.return_value = mock_gui_load_event_instance_for_timeout

        mock_gui_manager.webview_window = MagicMock()
        mock_shutdown_event.is_set.return_value = False
        with patch('comfy_launcher.__main__.event_publisher', mock_event_publisher):
            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                                  mock_server_log_path, mock_shutdown_event)

        mock_app_logger.error.assert_any_call("GUI window did not signal 'loaded' in time. Aborting app logic.")
        
        mock_event_publisher.publish.assert_any_call(
            launcher_main_module.AppEventType.APPLICATION_CRITICAL_ERROR,
            message="GUI did not load correctly. Check launcher logs."
        )
        mock_gui_manager.load_critical_error_page.assert_not_called()
        mock_server_manager.kill_process_on_port.assert_not_called()

    @patch('comfy_launcher.__main__.time.sleep', return_value=None)
    @patch('comfy_launcher.__main__.threading.Thread')
    @patch('comfy_launcher.__main__.app_shutdown_event', new_callable=lambda: MagicMock(spec=TestMainExecution.OriginalEventClass))
    @patch('comfy_launcher.__main__.threading.Event')
    def test_app_logic_thread_func_server_start_fails(self, mock_sut_event_constructor,
                                                      mock_global_app_shutdown_event,
                                                      mock_sut_thread_constructor,
                                                      mock_time_sleep,
                                                      MockTrayManager_class_level_param):
        mock_app_logger = MagicMock(spec=logging.Logger)
        mock_gui_manager = MagicMock(spec=GUIManager)
        mock_server_manager = MagicMock(spec=ServerManager)
        mock_server_log_path = Path("/fake/logs/server.log")
        mock_shutdown_event = mock_global_app_shutdown_event

        mock_event_publisher = MagicMock()
        mock_gui_load_event_instance_for_success = MagicMock(spec=self.OriginalEventClass, name="MockGuiLoadEventForSuccess")
        mock_gui_load_event_instance_for_success.wait.return_value = True
        mock_sut_event_constructor.return_value = mock_gui_load_event_instance_for_success

        mock_server_manager.start_server.return_value = None
        mock_gui_manager.webview_window = MagicMock()
        mock_shutdown_event.is_set.return_value = False
        
        initial_wait_return_values = [False, False, False]
        def temp_wait_side_effect(timeout):
            if initial_wait_return_values: return initial_wait_return_values.pop(0)
            return False
        mock_shutdown_event.wait.side_effect = temp_wait_side_effect
        
        with patch('comfy_launcher.__main__.settings') as mock_main_settings, \
             patch('comfy_launcher.__main__.event_publisher', mock_event_publisher):
            mock_main_settings.PORT = 8188
            app_logic_thread_func(mock_app_logger, mock_gui_manager, mock_server_manager,
                                  mock_server_log_path, mock_shutdown_event)

        mock_app_logger.error.assert_any_call("Failed to start ComfyUI server process. Aborting app logic.")
        
        mock_event_publisher.publish.assert_any_call(
            launcher_main_module.AppEventType.APPLICATION_CRITICAL_ERROR,
            message="Could not start the ComfyUI server. Please check the server.log file for details."
        )
        mock_gui_manager.load_error_page.assert_not_called()
        mock_sut_thread_constructor.assert_not_called()

class TestMainEventHandlers(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.logger_patcher = patch('comfy_launcher.__main__.launcher_logger', self.mock_logger)
        self.logger_patcher.start()

    def tearDown(self):
        self.logger_patcher.stop()

    @patch('comfy_launcher.__main__.app_shutdown_event')
    def test_handle_main_thread_quit_request(self, mock_app_shutdown_event):
        launcher_main_module._handle_main_thread_quit_request()
        mock_app_shutdown_event.set.assert_called_once()
        self.mock_logger.info.assert_any_call("MainThread Handler: APPLICATION_QUIT_REQUESTED received. Ensuring app_shutdown_event is set.")

    @patch('comfy_launcher.__main__.app_shutdown_event')
    @patch('comfy_launcher.__main__.gui_manager_instance')
    def test_handle_critical_error(self, mock_gui_manager_instance, mock_app_shutdown_event):
        test_message = "A critical error occurred!"
        launcher_main_module._handle_critical_error(test_message)
        
        mock_gui_manager_instance.load_critical_error_page.assert_called_once_with(test_message)
        mock_app_shutdown_event.set.assert_called_once()
        self.mock_logger.critical.assert_any_call(f"MainThread Handler: APPLICATION_CRITICAL_ERROR: {test_message}")

    def test_handle_app_logic_shutdown_complete(self):
        with patch('comfy_launcher.__main__._app_logic_completed_event') as mock_event:
            launcher_main_module._handle_app_logic_shutdown_complete()
            mock_event.set.assert_called_once()
        self.mock_logger.info.assert_any_call("MainThread Handler: APP_LOGIC_SHUTDOWN_COMPLETE received.")


if __name__ == '__main__':
    unittest.main()
