import webview
import threading
import time
from pathlib import Path
import os
import platform
import subprocess
from typing import Literal, Optional # Added Optional

if platform.system() == "Windows":
    try: import winreg
    except ImportError: winreg = None # Handle cases where winreg might not be available even on Windows
else:
    winreg = None

from .config import settings
from . import event_publisher, AppEventType # Import the global event publisher and event types

class GUIManager:
    # --- Constants for redirect loop ---
    REDIRECT_LOOP_MAX_WAIT_TIME = 120  # seconds
    REDIRECT_LOOP_CHECK_INTERVAL = 2  # seconds

    def __init__(self, app_name: str, window_width: int, window_height: int,
                 connect_host: str, port: int, assets_dir: Path, logger, server_manager):
        self.app_name = app_name
        self.window_width = window_width
        self.window_height = window_height
        self.connect_host = connect_host
        self.port = port
        self.assets_dir = assets_dir
        # Add path to React app build
        self.web_dist_dir = self.assets_dir.parent / "web_dist"
        self.logger = logger
        self.server_manager = server_manager
        self.webview_window: Optional[webview.Window] = None # Type hint for clarity
        self._loading_html_path: Optional[Path] = None
        self.is_window_loaded = threading.Event()
        self.is_window_shown = threading.Event() # Retained, might be useful
        self.application_is_quitting = False # Flag to indicate if app is quitting
        self.initial_load_done = False # To track if the very first load_html is done

        # Subscribe to events
        event_publisher.subscribe(AppEventType.APPLICATION_QUIT_REQUESTED, self.handle_application_quit_request)
        event_publisher.subscribe(AppEventType.APPLICATION_CRITICAL_ERROR, self.handle_critical_error_event)
        event_publisher.subscribe(AppEventType.SERVER_STOPPED_UNEXPECTEDLY, self.handle_server_stopped_unexpectedly_event)
        event_publisher.subscribe(AppEventType.SHOW_WINDOW_REQUEST, self.handle_show_window_request)


    def _on_closing(self, event=None) -> bool: # Added event parameter
        """
        Handles the window close event (e.g., user clicking 'X').
        Instead of quitting, it hides the window. The application continues
        running via the system tray.
        Return True to prevent the default window close behavior, allowing
        the event system to handle the actual shutdown and window destruction.
        """
        if event and hasattr(event, 'cancel'): # pywebview might pass an event object
            event.cancel = True # Prevent immediate closing if pywebview supports it this way

        self.logger.info("Window close event received (_on_closing). Publishing APPLICATION_QUIT_REQUESTED.")
        
        # Ensure the application knows it's quitting.
        # This flag is also set by handle_application_quit_request, but setting it here
        # ensures that if _on_closing is somehow called before the event is processed,
        # the state is correct.
        self.application_is_quitting = True
        
        event_publisher.publish(AppEventType.APPLICATION_QUIT_REQUESTED)
        
        # Hide the window as per the original intent of the test for _on_closing
        if self.webview_window:
            self.webview_window.hide()
        
        # Return True to prevent pywebview from closing the window immediately.
        # The actual window destruction will be handled by `handle_application_quit_request`
        # which is subscribed to the APPLICATION_QUIT_REQUESTED event.
        return True    def on_loaded(self): # Renamed from _on_loaded to match event subscription
        self.logger.info("🎉 Webview 'on_loaded' event fired!")
        current_url = self.webview_window.get_current_url() if self.webview_window else "N/A"
        self.logger.debug(f"Current URL in webview at on_loaded: {current_url}")

        if not self.initial_load_done:
            # This is the first load (React app)
            self.logger.debug("Initial React app loaded. Publishing GUI_WINDOW_CONTENT_LOADED event.")
            event_publisher.publish(AppEventType.GUI_WINDOW_CONTENT_LOADED)
            self.is_window_loaded.set()
            self.initial_load_done = True
            
            # Initialize React app with system theme
            theme = settings.LAUNCHER_THEME if settings.LAUNCHER_THEME in ["dark", "light"] else self._get_system_theme_preference()
            self.set_theme(theme)
            
        else:
            self.logger.debug("Webview 'loaded' event fired again (e.g., after page navigation).")
            if self.webview_window and current_url and "settings.html" in current_url:
                 self.logger.info("Settings page has been loaded into the webview.")
                 self._execute_js("if (typeof initializeSettingsPage === 'function') { initializeSettingsPage(); } else { console.error('initializeSettingsPage function not found on settings.html'); }")
            elif self.webview_window and current_url and ("index.html" in current_url or "web_dist" in current_url):
                 self.logger.info("React app has been (re)loaded into the webview.")
                 # Re-initialize theme if React app reloads
                 theme = settings.LAUNCHER_THEME if settings.LAUNCHER_THEME in ["dark", "light"] else self._get_system_theme_preference()
                 self.set_theme(theme)


    def on_shown(self): # Renamed from _on_shown
        self.logger.debug("Webview 'shown' event fired. Window is visible on screen.")
        event_publisher.publish(AppEventType.GUI_WINDOW_SHOWN)
        if not self.is_window_shown.is_set():
          self.is_window_shown.set()

    def _get_system_theme_preference(self) -> Literal["dark", "light"]:
        system_os = platform.system()
        theme: Literal["dark", "light"] = "light"
        if system_os == "Windows":
            if winreg:
                try:
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    if value == 0: theme = "dark"
                except Exception: self.logger.debug("Could not determine Windows dark mode via registry.", exc_info=True)
            else: self.logger.debug("winreg module not available for Windows theme detection.")
        elif system_os == "Darwin":
            try:
                cmd = ["defaults", "read", "-g", "AppleInterfaceStyle"]
                process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=2)
                if process.returncode == 0 and process.stdout.strip() == "Dark": theme = "dark"
                self.logger.debug(f"macOS theme detection: stdout='{process.stdout.strip()}', theme='{theme}'")
            except Exception as e: self.logger.error(f"Error detecting macOS theme: {e}.", exc_info=True)
        elif system_os == "Linux":
            try:
                cmd_xdg = ["gdbus", "call", "--session", "--dest", "org.freedesktop.portal.Desktop",
                           "--object-path", "/org/freedesktop/portal/desktop",
                           "--method", "org.freedesktop.portal.Settings.Read",
                           "org.freedesktop.appearance", "color-scheme"]
                process_xdg = subprocess.run(cmd_xdg, capture_output=True, text=True, check=True, timeout=2)
                output_xdg = process_xdg.stdout.strip().lower()
                if "'color-scheme': <uint32 1>" in output_xdg: theme = "dark"
                elif "'color-scheme': <uint32 2>" in output_xdg: theme = "light"
                self.logger.debug(f"Linux XDG portal theme: output='{output_xdg}', theme='{theme}'")
            except Exception as e_xdg: self.logger.info(f"XDG Portal for Linux theme failed: {e_xdg}.")
        else: self.logger.info(f"System theme detection not implemented for OS '{system_os}'.")
        self.logger.info(f"Determined system theme preference: '{theme}' for OS '{system_os}'.")
        return theme

    def _get_asset_content(self, relative_path: str, is_critical_fallback: bool = False) -> str:
        asset_path = self.assets_dir / relative_path
        try:
            with open(asset_path, "r", encoding="utf-8") as f: return f.read()
        except FileNotFoundError:
            self.logger.error(f"Asset file not found: {asset_path}")
            if is_critical_fallback:
                # Return a more user-friendly HTML fallback for critical assets
                self.logger.critical(f"Critical asset '{relative_path}' not found, and no fallback content available other than the hardcoded one.")
                return """<!DOCTYPE html><html><head><title>Error</title><style>body{font-family:sans-serif;text-align:center;padding:40px;background-color:#333;color:#fff;}h1{color:red;}</style></head>
                        <body><h1>Critical Error</h1>
                        <p>If you're seeing this, the application encountered a severe issue and could not load a required file.</p>
                        <p>Please check the launcher logs for more details.</p>
                        </body></html>"""
            return ""
        except Exception as e:
            self.logger.exception(f"Error reading asset file {asset_path}: {e}")
            return ""

    def _prepare_loading_html(self):
        self.logger.debug("Preparing full HTML structure for loading page...")
        html_template_content = self._get_asset_content("loading_base.html")
        if not html_template_content:
            self.logger.error("loading_base.html is missing. Attempting fallback_loading.html.")
            html_template_content = self._get_asset_content("fallback_loading.html", is_critical_fallback=True)
            if not html_template_content: raise FileNotFoundError("Both loading_base.html and fallback_loading.html missing.")

        js_content = self._get_asset_content("loading.js") or "window.updateStatus = console.log;"
        minimal_css_content = "body { margin: 0; padding: 20px; box-sizing: border-box; background-color: #1a1a1a; color: #f0f0f0; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; } .container { padding: 40px; background-color: #242424; border-radius: 8px; max-width: 500px; } .title { font-size: 1.8em; margin-bottom: 15px; } .accent { color: #0099ff; } #status-message { margin-top: 15px; color: #aaa; min-height: 1.2em; } .spinner { width: 50px; height: 50px; border: 5px solid #555; border-top-color: #0099ff; border-radius: 50%; margin: 0 auto 20px auto; animation: spin_simple 1.2s linear infinite; } @keyframes spin_simple { to { transform: rotate(360deg); } } #loader-wrapper { opacity: 1; } .fade-out { opacity: 0; transition: opacity 0.5s ease-out; }"
        content_with_css = html_template_content.replace("{CSS_CONTENT}", minimal_css_content)
        content_with_js = content_with_css.replace("{JS_CONTENT}", js_content)
        theme_class = settings.LAUNCHER_THEME if settings.LAUNCHER_THEME in ["dark", "light"] else self._get_system_theme_preference()
        final_content = content_with_js.replace("{THEME_CLASS}", theme_class)
        self._loading_html_path = self.assets_dir.parent / "loading_generated.html"
        try:
            with open(self._loading_html_path, "w", encoding="utf-8") as f: f.write(final_content)
            self.logger.debug(f"Generated loading HTML written to: {self._loading_html_path}")
        except Exception as e: self.logger.warning(f"Could not write generated loading HTML: {e}")
        return final_content    def _prepare_react_app_html(self):
        """
        Loads the built React app HTML file and returns its content.
        """
        react_html_path = self.web_dist_dir / "index.html"
        try:
            with open(react_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Convert paths to file:// URLs for local file access
            # Use pathlib for cross-platform path handling
            web_dist_url = react_html_path.parent.as_uri()
            
            # Update asset paths to absolute file URLs
            html_content = html_content.replace('src="./assets/', f'src="{web_dist_url}/assets/')
            html_content = html_content.replace('href="./assets/', f'href="{web_dist_url}/assets/')
            html_content = html_content.replace('href="/icon.png"', f'href="{web_dist_url}/icon.png"')
            
            self.logger.debug(f"Loaded React app HTML from: {react_html_path}")
            self.logger.debug(f"Web dist URL: {web_dist_url}")
            return html_content
        except FileNotFoundError:
            self.logger.error(f"React app HTML not found at: {react_html_path}")
            self.logger.info("Falling back to legacy loading page...")
            # Fallback to old loading page
            return self._prepare_loading_html()
        except Exception as e:
            self.logger.error(f"Error loading React app HTML: {e}")
            self.logger.info("Falling back to legacy loading page...")
            return self._prepare_loading_html()

    def _execute_js(self, js_code: str):
        if self.webview_window:
            try:
                self.webview_window.evaluate_js(js_code)
            except Exception as e:
                self.logger.error(f"Error executing JavaScript in webview: {e}", exc_info=True)
        else:
            self.logger.debug("Cannot execute JS, webview_window is None.")

    def set_status(self, message: str):
        self.logger.info(f"[GUI STATUS] {message}")
        escaped_message = message.replace("\\", "\\\\").replace("'", "\\'")
        self._execute_js(f"if(typeof window.updateStatus === 'function') window.updateStatus('{escaped_message}');")

    def set_log_path(self, path: str):
        """Set the log file path in the React app"""
        escaped_path = path.replace("\\", "\\\\").replace("'", "\\'")
        self._execute_js(f"if(typeof window.setLogPath === 'function') window.setLogPath('{escaped_path}');")

    def set_theme(self, theme: str):
        """Set the theme in the React app"""
        if theme in ['light', 'dark']:
            self._execute_js(f"if(typeof window.setTheme === 'function') window.setTheme('{theme}');")

    def py_toggle_devtools(self):
        if self.webview_window: # pragma: no branch
            if settings.DEBUG: self.webview_window.toggle_devtools()
            else: self.logger.info("Developer Tools are disabled (DEBUG mode is off).")    def prepare_and_launch_gui(self, shutdown_event_for_critical_error: Optional[threading.Event] = None):
        try:
            html_content = self._prepare_react_app_html()
            if not html_content: raise RuntimeError("Could not prepare HTML for React app.")
            self.logger.info("🪟 Creating GUI window by loading HTML content directly...")
            self.webview_window = webview.create_window(
                self.app_name, html=html_content, width=self.window_width,
                height=self.window_height, resizable=True,
                confirm_close=False # Avoid pywebview's own confirm dialog; we handle hide/close in _on_closing
            )
            self.webview_window.events.loaded += self.on_loaded
            self.webview_window.events.shown += self.on_shown
            self.webview_window.events.closing += self._on_closing # Add closing handler

            if settings.DEBUG:
                try: self.webview_window.expose(self.py_toggle_devtools)
                except Exception as e: self.logger.error(f"Failed to expose py_toggle_devtools: {e}")
            self.logger.info("✅ Window created. Events subscribed & functions exposed.")
        except Exception as e:
            self.logger.critical(f"CRITICAL - Failed to create or launch window: {e}", exc_info=True)
            if shutdown_event_for_critical_error:
                shutdown_event_for_critical_error.set()
            # Re-raise or handle as appropriate, for now, it will propagate up if not caught by main
            raise

    def handle_application_quit_request(self):
        """
        Handler for the APPLICATION_QUIT_REQUESTED event.
        Sets the quitting flag and attempts to close the window programmatically to trigger its destruction.
        """
        self.logger.info("GUIManager Handler: APPLICATION_QUIT_REQUESTED received. Proceeding with window destruction.")
        self.application_is_quitting = True
        
        window_to_destroy = self.webview_window
        if window_to_destroy:
            try:
                self.logger.debug(f"Destroying window: {window_to_destroy}")
                self.webview_window = None # Nullify before destroying
                window_to_destroy.destroy() # Call destroy() on the window instance
                self.logger.info("Webview window destroyed by handle_application_quit_request.")
            except Exception as e:
                self.logger.error(f"Error destroying window in handle_application_quit_request: {e}", exc_info=True)
        # No need to call window.close() JS anymore, as this handler now directly destroys.    def load_error_page(self, message: str):
        self.logger.error(f"Loading error page with message: {message}")
        # Use React app's error handling instead of loading new HTML
        escaped_message = message.replace("\\", "\\\\").replace("'", "\\'")
        self._execute_js(f"if(typeof window.showError === 'function') window.showError('{escaped_message}');")

    def load_critical_error_page(self, message: str):
        self.logger.critical(f"Loading critical error page with message: {message}")
        # Use React app's critical error handling instead of loading new HTML
        escaped_message = message.replace("\\", "\\\\").replace("'", "\\'")
        self._execute_js(f"if(typeof window.showCriticalError === 'function') window.showCriticalError('{escaped_message}');")


    def redirect_when_ready_loop(self, stop_event: threading.Event,
                                 overall_shutdown_event: threading.Event):
        self.logger.info("Redirect loop: Started.")
        start_time = time.time()

        while not stop_event.is_set() and not overall_shutdown_event.is_set():
            if time.time() - start_time > self.REDIRECT_LOOP_MAX_WAIT_TIME:
                self.logger.warning("Redirect loop: Max wait time exceeded for server availability.")
                if not overall_shutdown_event.is_set(): # Avoid changing page if already shutting down
                    self.load_error_page("ComfyUI server did not become available in time. Please check server logs.")
                break

            # Call wait_for_server_availability without the timeout argument
            if self.server_manager.wait_for_server_availability(retries=1, delay=0.1): # Use small retry/delay for quick check
                target_url = f"http://{self.connect_host}:{self.port}"
                self.logger.info(f"Redirect loop: Server is available. Attempting to redirect webview to {target_url}")
                if self.webview_window:
                    self._execute_js("if(typeof window.fadeOutLoading === 'function') window.fadeOutLoading();")
                    time.sleep(1.5) # Give fade out animation time
                    if not overall_shutdown_event.is_set(): # Check again before loading URL
                        self.webview_window.load_url(target_url)
                else:
                    self.logger.error("Redirect loop: Webview window is not available for redirection.")
                self.set_status("Connected to ComfyUI.") # Set status on successful connection
                break
            else:
                # Update log message to reflect the actual retry interval
                self.logger.debug(f"Redirect loop: Server not yet available. Retrying in {self.REDIRECT_LOOP_CHECK_INTERVAL}s...")

            if not self.webview_window or getattr(self.webview_window, 'gui', None) is None:
                self.logger.info("Redirect loop: Webview window no longer exists. Stopping.")
                break
            # Wait for 'check_interval', breaking if stop_event is set.
            # The main while loop condition handles overall_shutdown_event.
            if stop_event.wait(self.REDIRECT_LOOP_CHECK_INTERVAL):
                self.logger.info("Redirect loop: stop_event set during wait. Exiting loop.")
                break
        self.logger.info("Redirect loop: Exiting.")


    def start_webview_blocking(self):
        if self.webview_window:
            self.logger.debug("Starting webview event loop (blocking)...")
            webview.start(debug=settings.DEBUG, private_mode=False, http_server=False) # Diagnostic change
            self.logger.debug("Webview event loop finished.")
        else:
            self.logger.error("Cannot start webview: window was not created.")

    # --- Event Handlers ---
    def handle_critical_error_event(self, message: str):
        self.logger.info(f"Event Handler: Received APPLICATION_CRITICAL_ERROR: {message}")
        self.load_critical_error_page(message)

    def handle_server_stopped_unexpectedly_event(self, pid: int, returncode: int):
        # Import app_shutdown_event locally to avoid circular dependency at module level if __main__ imports GUIManager
        from comfy_launcher.__main__ import app_shutdown_event as global_app_shutdown_event
        if global_app_shutdown_event.is_set():
            self.logger.info(f"Event Handler: Received SERVER_STOPPED_UNEXPECTEDLY (PID: {pid}, Code: {returncode}), but app is already shutting down. No error page displayed.")
            return
        
        self.logger.error(f"Event Handler: Received SERVER_STOPPED_UNEXPECTEDLY (PID: {pid}, Code: {returncode}). Displaying error page.")
        error_message = f"ComfyUI server (PID: {pid}) stopped unexpectedly with code {returncode}. Check server.log."
        self.load_error_page(error_message)

    def handle_show_window_request(self):
        self.logger.info("Event Handler: Received SHOW_WINDOW_REQUEST. Attempting to show and activate GUI window.")
        if self.webview_window:
            self.webview_window.show()
            if hasattr(self.webview_window, 'activate'): # Some platforms might not have activate
                self.webview_window.activate()
            # Publishing SHOW_WINDOW_REQUEST_RELAYED_TO_GUI is not strictly necessary if this is the final handler
            # but can be useful for logging or if other components need to know.
            # event_publisher.publish(AppEventType.SHOW_WINDOW_REQUEST_RELAYED_TO_GUI)
        else:
            self.logger.warning("Event Handler: Received SHOW_WINDOW_REQUEST, but webview_window is None. Cannot show.")
