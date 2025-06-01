import unittest
from unittest.mock import patch, MagicMock, call, mock_open, ANY
from pathlib import Path
import threading
import time 
import platform # For mocking platform.system() in new tests
import subprocess # For mocking subprocess.run and its exceptions

import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.gui_manager import GUIManager
from comfy_launcher.config import settings # Using the actual settings object
from comfy_launcher.event_system import AppEventType # For testing event publishing

import logging
logging.disable(logging.CRITICAL)

class TestGuiManager(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.mock_server_manager = MagicMock()
        
        self.current_settings = settings 
        self.original_debug_state = self.current_settings.DEBUG 
        # settings.DEBUG will be patched within tests using `with patch(...)` for isolation

        self.gui_manager = GUIManager(
            app_name=self.current_settings.APP_NAME,
            window_width=self.current_settings.WINDOW_WIDTH,
            window_height=self.current_settings.WINDOW_HEIGHT,
            connect_host=self.current_settings.EFFECTIVE_CONNECT_HOST, # Changed from host
            port=self.current_settings.PORT,
            assets_dir=self.current_settings.ASSETS_DIR, 
            logger=self.mock_logger,
            server_manager=self.mock_server_manager
        )
        # self.gui_manager.webview_window will be set by prepare_and_launch_gui
        # and will be a mock returned by mock_webview_module.create_window

    def tearDown(self):
        # Restore global settings.DEBUG if it was changed by a test directly
        # This ensures that if a test patches it, it's restored.
        settings.DEBUG = self.original_debug_state


    def test_initialization(self):
        self.assertEqual(self.gui_manager.app_name, self.current_settings.APP_NAME)
        self.assertIsInstance(self.gui_manager.is_window_loaded, threading.Event)
        self.assertIsInstance(self.gui_manager.is_window_shown, threading.Event)

    @patch('comfy_launcher.gui_manager.GUIManager._get_asset_content')
    @patch('comfy_launcher.gui_manager.GUIManager._get_system_theme_preference')
    @patch('comfy_launcher.gui_manager.settings') # Patch settings used by GUIManager
    def test_prepare_loading_html_content_generation(self, mock_settings_gui, mock_get_system_theme, mock_get_asset_content_method):
        def get_asset_side_effect(relative_path, is_critical_fallback=False):
            if Path(relative_path).name == "loading_base.html":
                return "<html><head><style>{CSS_CONTENT}</style></head><body class=\"{THEME_CLASS}\"><script>{JS_CONTENT}</script></body></html>"
            elif Path(relative_path).name == "loading.js":
                return "window.test_js_loaded = true;"
            elif Path(relative_path).name == "fallback_loading.html": # For fallback test
                return "Fallback HTML {THEME_CLASS} {CSS_CONTENT} {JS_CONTENT}"
            return "" # Default for any other unexpected calls
        mock_get_asset_content_method.side_effect = get_asset_side_effect
        
        # Test scenarios for different LAUNCHER_THEME settings
        theme_scenarios = [
            ("system_light", "system", "light", "light"), # LAUNCHER_THEME, _get_system_theme_preference return, expected class
            ("system_dark", "system", "dark", "dark"),
            ("light_explicit", "light", "light", "light"), # _get_system_theme_preference mock return (won't be called)
            ("dark_explicit", "dark", "dark", "dark")    # _get_system_theme_preference mock return (won't be called)
        ]

        for name, theme_setting, system_theme_return, expected_theme_class in theme_scenarios:
            with self.subTest(scenario=name):
                mock_settings_gui.LAUNCHER_THEME = theme_setting
                mock_get_system_theme.return_value = system_theme_return
                
                # Reset mocks that are called inside the loop
                mock_get_asset_content_method.reset_mock()
                mock_get_asset_content_method.side_effect = get_asset_side_effect # Re-assign side effect
                mock_get_system_theme.reset_mock() # Reset for calls within _prepare_loading_html
                mock_get_system_theme.return_value = system_theme_return # Re-assign for this sub-test

                with patch('builtins.open', mock_open()) as mock_file_write:
                    html_string_result = self.gui_manager._prepare_loading_html()

                mock_get_asset_content_method.assert_any_call("loading_base.html")
                mock_get_asset_content_method.assert_any_call("loading.js")
                
                css_call_found = False
                for acall in mock_get_asset_content_method.call_args_list:
                    if acall[0][0] == "loading.css": 
                        css_call_found = True
                        break
                self.assertFalse(css_call_found, "_get_asset_content should not be called for 'loading.css'")
                
                self.assertIn("body {", html_string_result) 
                self.assertIn("@keyframes spin_simple", html_string_result)
                self.assertIn("window.test_js_loaded = true;", html_string_result)
                self.assertIn(f'class="{expected_theme_class}"', html_string_result)
                
                if theme_setting == "system":
                    mock_get_system_theme.assert_called_once()
                else:
                    mock_get_system_theme.assert_not_called() # Should not be called if theme is explicit
                
                expected_written_path = self.gui_manager.assets_dir.parent / "loading_generated.html"
                mock_file_write.assert_called_once_with(expected_written_path, "w", encoding="utf-8")

    @patch('comfy_launcher.gui_manager.platform.system')
    @patch('comfy_launcher.gui_manager.winreg', create=True) # create=True because winreg might be None in SUT
    @patch('comfy_launcher.gui_manager.subprocess.run')
    def test_get_system_theme_preference_windows(self, mock_subprocess_run, mock_winreg, mock_platform_system):
        mock_platform_system.return_value = "Windows"
        
        # Test Windows Dark Mode
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (0, None) # 0 for AppsUseLightTheme means dark
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "dark")
        mock_winreg.ConnectRegistry.assert_called_once_with(None, mock_winreg.HKEY_CURRENT_USER)
        mock_winreg.OpenKey.assert_called_once_with(mock_winreg.ConnectRegistry.return_value, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        mock_winreg.CloseKey.assert_called_once_with(mock_key)


        # Test Windows Light Mode
        mock_winreg.reset_mock()
        mock_key_light = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key_light
        mock_winreg.QueryValueEx.return_value = (1, None) # 1 for AppsUseLightTheme means light
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")

        # Test Windows Registry Error
        mock_winreg.reset_mock()
        mock_winreg.OpenKey.side_effect = Exception("Registry boom")
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light") # Should default to light
        self.mock_logger.debug.assert_any_call("Could not determine Windows dark mode via registry.", exc_info=True) # Original log

        # Test winreg module not available (simulating non-Windows import failure, though platform is mocked to Windows)
        # This tests the `if winreg:` check within the Windows block of _get_system_theme_preference
        mock_winreg.reset_mock()
        with patch('comfy_launcher.gui_manager.winreg', None): # Temporarily make winreg None for this specific check
             self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
             self.mock_logger.debug.assert_any_call("winreg module not available for Windows theme detection.")


    @patch('comfy_launcher.gui_manager.platform.system', return_value="Darwin") # macOS
    @patch('comfy_launcher.gui_manager.subprocess.run')
    def test_get_system_theme_preference_macos(self, mock_subprocess_run, mock_platform_system):
        # Test macOS Dark Mode
        mock_process_dark = MagicMock()
        mock_process_dark.returncode = 0
        mock_process_dark.stdout = "Dark\n"
        mock_subprocess_run.return_value = mock_process_dark
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "dark")
        mock_subprocess_run.assert_called_once_with(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True, text=True, check=False, timeout=2
        )

        # Test macOS Light Mode (key not found or different value)
        mock_subprocess_run.reset_mock()
        mock_process_light = MagicMock()
        mock_process_light.returncode = 1 # Simulates key not found
        mock_process_light.stdout = ""
        mock_subprocess_run.return_value = mock_process_light
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        
        # Test macOS 'defaults' command not found
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = FileNotFoundError
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        self.mock_logger.error.assert_any_call(f"Error detecting macOS theme: {FileNotFoundError()}.", exc_info=True)

        # Test macOS 'defaults' command timeout
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="defaults", timeout=2)
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        self.mock_logger.error.assert_any_call(f"Error detecting macOS theme: {subprocess.TimeoutExpired('defaults', 2)}.", exc_info=True)

    @patch('comfy_launcher.gui_manager.platform.system', return_value="Linux")
    @patch('comfy_launcher.gui_manager.subprocess.run')
    def test_get_system_theme_preference_linux(self, mock_subprocess_run, mock_platform_system):
        expected_xdg_cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.freedesktop.portal.Desktop",
            "--object-path", "/org/freedesktop/portal/desktop",
            "--method", "org.freedesktop.portal.Settings.Read",
            "org.freedesktop.appearance", "color-scheme"
        ]
        
        # Test Linux Dark Mode via XDG Portal
        mock_process_xdg_dark = MagicMock()
        mock_process_xdg_dark.stdout = "(<{'color-scheme': <uint32 1>}>,)" # Dark
        mock_process_xdg_dark.returncode = 0 # check=True means this won't raise CalledProcessError
        mock_subprocess_run.return_value = mock_process_xdg_dark
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "dark")
        mock_subprocess_run.assert_called_once_with(
            expected_xdg_cmd, capture_output=True, text=True, check=True, timeout=2
        )

        # Test Linux Light Mode via XDG Portal
        mock_subprocess_run.reset_mock()
        mock_process_xdg_light = MagicMock()
        mock_process_xdg_light.stdout = "(<{'color-scheme': <uint32 2>}>,)" # Light
        mock_process_xdg_light.returncode = 0
        mock_subprocess_run.return_value = mock_process_xdg_light
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")

        # Test Linux XDG Portal command fails (e.g., gdbus not found)
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = FileNotFoundError
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        self.mock_logger.info.assert_any_call(f"XDG Portal for Linux theme failed: {FileNotFoundError()}.")

        # Test Linux XDG Portal command returns error
        mock_subprocess_run.reset_mock()
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=expected_xdg_cmd)
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        self.mock_logger.info.assert_any_call(f"XDG Portal for Linux theme failed: {subprocess.CalledProcessError(1, expected_xdg_cmd)}.")

    @patch('comfy_launcher.gui_manager.platform.system', return_value="Solaris") # Unknown OS
    def test_get_system_theme_preference_unknown_os(self, mock_platform_system):
        self.assertEqual(self.gui_manager._get_system_theme_preference(), "light")
        self.mock_logger.info.assert_any_call("System theme detection not implemented for OS 'Solaris'.")

    
    @patch('comfy_launcher.gui_manager.webview')
    def test_prepare_and_launch_gui_creates_window(self, mock_webview_module):
        self.gui_manager._prepare_loading_html = MagicMock(return_value="<html>Mocked Content</html>")
        
        mock_window_instance = MagicMock(name="MockWindowInstance")
        
        loaded_event_mock = MagicMock(name="LoadedEventMock")
        shown_event_mock = MagicMock(name="ShownEventMock")
        closing_event_mock = MagicMock(name="ClosingEventMock")
        mock_window_instance.events = MagicMock(loaded=loaded_event_mock, shown=shown_event_mock, closing=closing_event_mock)
        
        mock_webview_module.create_window.return_value = mock_window_instance

        with patch('comfy_launcher.gui_manager.settings.DEBUG', True):
            self.gui_manager.prepare_and_launch_gui()

            self.gui_manager._prepare_loading_html.assert_called_once()
            mock_webview_module.create_window.assert_called_once_with(
                self.gui_manager.app_name,
                html="<html>Mocked Content</html>",
                width=self.gui_manager.window_width,
                height=self.gui_manager.window_height,
                resizable=True,
                confirm_close=False 
            )
            loaded_event_mock.__iadd__.assert_called_with(self.gui_manager.on_loaded)
            shown_event_mock.__iadd__.assert_called_with(self.gui_manager.on_shown)
            closing_event_mock.__iadd__.assert_called_with(self.gui_manager._on_closing)
            mock_window_instance.expose.assert_called_with(self.gui_manager.py_toggle_devtools)
            self.assertEqual(mock_window_instance.expose.call_count, 1, "Only py_toggle_devtools should be exposed when DEBUG=True")

        self.gui_manager._prepare_loading_html.reset_mock()
        mock_webview_module.create_window.reset_mock()
        loaded_event_mock.reset_mock() 
        shown_event_mock.reset_mock() 
        closing_event_mock.reset_mock()
        mock_window_instance.expose.reset_mock()

        with patch('comfy_launcher.gui_manager.settings.DEBUG', False):
            self.gui_manager.prepare_and_launch_gui()
            mock_window_instance.expose.assert_not_called()


    def test_on_loaded_sets_event_first_time(self):
        self.gui_manager.is_window_loaded.clear() 
        self.gui_manager.webview_window = MagicMock() 
        self.gui_manager.webview_window.get_current_url.return_value = str(self.current_settings.ASSETS_DIR.parent / "loading_generated.html")

        self.gui_manager.on_loaded()

        self.assertTrue(self.gui_manager.is_window_loaded.is_set())
        self.mock_logger.debug.assert_any_call("Initial window content loaded. Publishing GUI_WINDOW_CONTENT_LOADED event.")

    def test_on_loaded_subsequent_times_settings_page(self):
        self.gui_manager.is_window_loaded.set() 
        self.gui_manager.initial_load_done = True # Explicitly set for subsequent load
        self.gui_manager.webview_window = MagicMock()
        self.gui_manager.webview_window.get_current_url.return_value = "settings.html" 
        
        self.gui_manager._execute_js = MagicMock()

        self.gui_manager.on_loaded()
        
        self.mock_logger.info.assert_any_call("🎉 Webview 'on_loaded' event fired!") # Check this first
        self.mock_logger.info.assert_any_call("Settings page has been loaded into the webview.")
        self.gui_manager._execute_js.assert_called_with("if (typeof initializeSettingsPage === 'function') { initializeSettingsPage(); } else { console.error('initializeSettingsPage function not found on settings.html'); }")


    def test_set_status_calls_execute_js(self):
        self.gui_manager.webview_window = MagicMock() 
        self.gui_manager._execute_js = MagicMock() 
        test_message = "Test Status Update"
        
        self.gui_manager.set_status(test_message)
        
        escaped_message = test_message.replace("\\", "\\\\").replace("'", "\\'")
        self.gui_manager._execute_js.assert_called_once_with(
            f"if(typeof window.updateStatus === 'function') window.updateStatus('{escaped_message}');"
        )

    @patch('comfy_launcher.gui_manager.webview')
    def test_start_webview_blocking_calls_webview_start(self, mock_webview_module):
        self.gui_manager.webview_window = MagicMock() 
        with patch('comfy_launcher.gui_manager.settings.DEBUG', True):
            self.gui_manager.start_webview_blocking()
            mock_webview_module.start.assert_called_once_with(debug=True, private_mode=False, http_server=False)

        mock_webview_module.start.reset_mock() 
        
        with patch('comfy_launcher.gui_manager.settings.DEBUG', False):
            self.gui_manager.start_webview_blocking()
            mock_webview_module.start.assert_called_once_with(debug=False, private_mode=False, http_server=False)

    def test_py_toggle_devtools_debug_true(self):
        self.gui_manager.webview_window = MagicMock() 
        with patch('comfy_launcher.gui_manager.settings.DEBUG', True):
            self.gui_manager.py_toggle_devtools()
            self.gui_manager.webview_window.toggle_devtools.assert_called_once()
            # The log message "Toggling Developer Tools via F12..." was removed from the source.

    def test_py_toggle_devtools_debug_false(self):
        self.gui_manager.webview_window = MagicMock() 
        with patch('comfy_launcher.gui_manager.settings.DEBUG', False):
            self.gui_manager.py_toggle_devtools()
            self.gui_manager.webview_window.toggle_devtools.assert_not_called()
            self.mock_logger.info.assert_any_call("Developer Tools are disabled (DEBUG mode is off).")

    @patch('comfy_launcher.gui_manager.event_publisher.publish')
    def test_on_closing_event_handler(self, mock_event_publish):
        self.gui_manager.webview_window = MagicMock(name="MockWebviewWindow")
        mock_gui_event = MagicMock(name="MockGuiClosingEvent")
        mock_gui_event.cancel = MagicMock()

        self.gui_manager._on_closing(event=mock_gui_event) # Pass as keyword arg

        self.assertEqual(mock_gui_event.cancel, True, "event.cancel should have been set to True")
        self.gui_manager.webview_window.hide.assert_called_once()
        mock_event_publish.assert_called_once_with(AppEventType.APPLICATION_QUIT_REQUESTED)
        self.mock_logger.info.assert_called_once_with(
            "Window close event received (_on_closing). Publishing APPLICATION_QUIT_REQUESTED."
        )
        # Ensure is_window_shown is cleared
        self.assertFalse(self.gui_manager.is_window_shown.is_set(), "is_window_shown should be cleared when window is hidden.")

    def test_on_shown_handler(self):
        self.gui_manager.is_window_shown.clear() # Ensure it's not set initially
        
        self.gui_manager.on_shown() # The method being tested

        self.assertTrue(self.gui_manager.is_window_shown.is_set())
        self.mock_logger.debug.assert_called_once_with("Webview 'shown' event fired. Window is visible on screen.")

    @patch('comfy_launcher.gui_manager.event_publisher.publish') # If it publishes events
    def test_handle_critical_error_event_loads_page(self, mock_event_publish):
        test_error_message = "Something went terribly wrong!"
        self.gui_manager.load_critical_error_page = MagicMock() # Mock the method that loads the page

        # Simulate the event being handled
        self.gui_manager.handle_critical_error_event(message=test_error_message)

        self.gui_manager.load_critical_error_page.assert_called_once_with(test_error_message)
        self.mock_logger.info.assert_any_call(f"Event Handler: Received APPLICATION_CRITICAL_ERROR: {test_error_message}")

    # Patch where app_shutdown_event is imported and used within the SUT method
    @patch('comfy_launcher.__main__.app_shutdown_event') 
    def test_handle_server_stopped_unexpectedly_event_not_shutting_down(self, mock_app_shutdown_event):
        mock_app_shutdown_event.is_set.return_value = False
        self.gui_manager.load_error_page = MagicMock()
        test_pid = 123
        test_returncode = 1

        self.gui_manager.handle_server_stopped_unexpectedly_event(pid=test_pid, returncode=test_returncode)

        expected_message = f"ComfyUI server (PID: {test_pid}) stopped unexpectedly with code {test_returncode}. Check server.log."
        self.gui_manager.load_error_page.assert_called_once_with(expected_message)
        self.mock_logger.error.assert_any_call(f"Event Handler: Received SERVER_STOPPED_UNEXPECTEDLY (PID: {test_pid}, Code: {test_returncode}). Displaying error page.")

    @patch('comfy_launcher.__main__.app_shutdown_event')
    def test_handle_server_stopped_unexpectedly_event_already_shutting_down(self, mock_app_shutdown_event):
        mock_app_shutdown_event.is_set.return_value = True
        self.gui_manager.load_error_page = MagicMock()
        test_pid = 456
        test_returncode = 0

        self.gui_manager.handle_server_stopped_unexpectedly_event(pid=test_pid, returncode=test_returncode)

        self.gui_manager.load_error_page.assert_not_called()
        self.mock_logger.info.assert_any_call(f"Event Handler: Received SERVER_STOPPED_UNEXPECTEDLY (PID: {test_pid}, Code: {test_returncode}), but app is already shutting down. No error page displayed.")

    @patch('comfy_launcher.gui_manager.event_publisher.publish')
    def test_handle_show_window_request_window_exists(self, mock_event_publish):
        self.gui_manager.webview_window = MagicMock(name="MockWebviewWindow")
        self.gui_manager.webview_window.activate = MagicMock() # Ensure activate method exists

        self.gui_manager.handle_show_window_request()

        self.gui_manager.webview_window.show.assert_called_once()
        self.gui_manager.webview_window.activate.assert_called_once()
        # Publishing SHOW_WINDOW_REQUEST_RELAYED_TO_GUI is optional in SUT, so don't assert strictly
        # mock_event_publish.assert_called_once_with(AppEventType.SHOW_WINDOW_REQUEST_RELAYED_TO_GUI)
        self.mock_logger.info.assert_any_call("Event Handler: Received SHOW_WINDOW_REQUEST. Attempting to show and activate GUI window.")

    @patch('comfy_launcher.gui_manager.event_publisher.publish')
    def test_handle_show_window_request_window_none(self, mock_event_publish):
        self.gui_manager.webview_window = None

        self.gui_manager.handle_show_window_request()

        mock_event_publish.assert_not_called() # Should not relay if no window
        self.mock_logger.warning.assert_any_call("Event Handler: Received SHOW_WINDOW_REQUEST, but webview_window is None. Cannot show.")

    @patch('comfy_launcher.gui_manager.time.sleep', return_value=None) # Mock sleep to speed up test
    def test_redirect_loop_server_available_redirects_and_sets_status(self, mock_sleep):
        self.gui_manager.webview_window = MagicMock()
        self.gui_manager.webview_window.load_url = MagicMock()
        self.gui_manager.set_status = MagicMock()
        self.mock_server_manager.wait_for_server_availability.return_value = True
        
        mock_redirect_stop_event = threading.Event()
        mock_shutdown_event = threading.Event()

        # To exit the loop after one successful iteration
        self.gui_manager.webview_window.load_url.side_effect = lambda url: mock_redirect_stop_event.set()

        self.gui_manager.redirect_when_ready_loop(mock_redirect_stop_event, mock_shutdown_event)

        # The SUT calls wait_for_server_availability with specific retries/delay now
        self.mock_server_manager.wait_for_server_availability.assert_called_once_with(retries=1, delay=0.1)
        self.gui_manager.webview_window.load_url.assert_called_once_with(f"http://{self.gui_manager.connect_host}:{self.gui_manager.port}")
        self.gui_manager.set_status.assert_called_with("Connected to ComfyUI.")
        self.mock_logger.info.assert_any_call(f"Redirect loop: Server is available. Attempting to redirect webview to http://{self.gui_manager.connect_host}:{self.gui_manager.port}")

    @patch('comfy_launcher.gui_manager.time.sleep', return_value=None)
    @patch.object(GUIManager, 'load_error_page') # Patch the method
    def test_redirect_loop_server_timeout_sets_error_status(self, mock_load_error_page, mock_sleep):
        self.gui_manager.webview_window = MagicMock()
        self.gui_manager.webview_window.load_url = MagicMock()
        self.gui_manager.set_status = MagicMock()
        self.mock_server_manager.wait_for_server_availability.return_value = False # Simulate timeout

        mock_redirect_stop_event = threading.Event()
        mock_shutdown_event = threading.Event()

        # To exit the loop after one failed iteration
        # The loop now has a max_wait_time, so we can let it timeout naturally or force stop_event
        self.gui_manager.REDIRECT_LOOP_MAX_WAIT_TIME = 0.1 # Force quick timeout for test
        # self.mock_server_manager.wait_for_server_availability.side_effect = lambda **kwargs: mock_redirect_stop_event.set() or False

        self.gui_manager.redirect_when_ready_loop(mock_redirect_stop_event, mock_shutdown_event)

        self.gui_manager.webview_window.load_url.assert_not_called()
        mock_load_error_page.assert_called_with("ComfyUI server did not become available in time. Please check server logs.")
        self.mock_logger.warning.assert_any_call("Redirect loop: Max wait time exceeded for server availability.")

    def test_get_asset_content_file_not_found_non_critical(self):
        # Mock assets_dir to control path resolution
        mock_assets_dir = MagicMock(spec=Path)
        mock_non_existent_path = MagicMock(spec=Path)
        mock_non_existent_path.exists.return_value = False
        mock_non_existent_path.name = "non_existent.js" # For logging
        mock_assets_dir.__truediv__.return_value = mock_non_existent_path
        self.gui_manager.assets_dir = mock_assets_dir

        content = self.gui_manager._get_asset_content("non_existent.js")

        self.assertEqual(content, "")
        self.mock_logger.error.assert_any_call(f"Asset file not found: {mock_non_existent_path}")

    def test_get_asset_content_file_not_found_critical_fallback(self):
        mock_assets_dir = MagicMock(spec=Path)
        mock_non_existent_path = MagicMock(spec=Path)
        mock_non_existent_path.exists.return_value = False
        mock_non_existent_path.name = "critical_asset.html"
        mock_assets_dir.__truediv__.return_value = mock_non_existent_path
        self.gui_manager.assets_dir = mock_assets_dir

        content = self.gui_manager._get_asset_content("critical_asset.html", is_critical_fallback=True)

        self.assertIn("<h1>Critical Error</h1>", content) # Check for part of the fallback HTML
        self.assertIn("If you're seeing this, the application encountered a severe issue", content)
        self.mock_logger.error.assert_any_call(f"Asset file not found: {mock_non_existent_path}")
        self.mock_logger.critical.assert_any_call(f"Critical asset 'critical_asset.html' not found, and no fallback content available other than the hardcoded one.")

    def test_execute_js_no_window(self):
        self.gui_manager.webview_window = None
        self.gui_manager._execute_js("console.log('test');")
        self.mock_logger.debug.assert_any_call("Cannot execute JS, webview_window is None.")

    def test_execute_js_webview_error(self):
        self.gui_manager.webview_window = MagicMock()
        self.gui_manager.webview_window.evaluate_js.side_effect = Exception("JS execution failed")
        
        self.gui_manager._execute_js("test_function();")
        
        self.mock_logger.error.assert_any_call("Error executing JavaScript in webview: JS execution failed", exc_info=True)


if __name__ == '__main__':
    unittest.main()
