import webview
import threading
import time
from pathlib import Path
import os
import platform
import subprocess
from typing import Literal, Optional # Added Optional

if platform.system() == "Windows":
    import winreg
else:
    winreg = None

from .config import settings

class GUIManager:
    def __init__(self, app_name: str, window_width: int, window_height: int,
                 connect_host: str, port: int, assets_dir: Path, logger, server_manager):
        self.app_name = app_name
        self.window_width = window_width
        self.window_height = window_height
        self.connect_host = connect_host
        self.port = port
        self.assets_dir = assets_dir
        self.logger = logger
        self.server_manager = server_manager
        self.webview_window: Optional[webview.Window] = None # Type hint for clarity
        self._loading_html_path: Optional[Path] = None
        self.is_window_loaded = threading.Event()
        self.is_window_shown = threading.Event() # Retained, might be useful
        self.initial_load_done = False # To track if the very first load_html is done

    def _on_closing(self) -> bool:
        """
        Handles the window close event (e.g., user clicking 'X').
        Instead of quitting, it hides the window. The application continues
        running via the system tray.
        Return True to prevent the default window close behavior.
        """
        self.logger.info("GUI Manager: Window close requested by user.")
        if self.webview_window:
            self.webview_window.hide()
            self.logger.info("GUI Manager: Window hidden. Application continues in tray.")
        return True # Prevent default webview close behavior

    def on_loaded(self): # Renamed from _on_loaded to match event subscription
        self.logger.info("🎉 Webview 'on_loaded' event fired!")
        current_url = self.webview_window.get_current_url() if self.webview_window else "N/A"
        self.logger.debug(f"Current URL in webview at on_loaded: {current_url}")

        if not self.initial_load_done:
            # This is the first load (e.g. loading.html)
            self.logger.debug("Signaling that initial window content is loaded.")
            self.is_window_loaded.set()
            self.initial_load_done = True
        else:
            self.logger.debug("Webview 'loaded' event fired again (e.g., after page navigation).")
            if self.webview_window and current_url and "settings.html" in current_url:
                 self.logger.info("Settings page has been loaded into the webview.")
                 self._execute_js("if (typeof initializeSettingsPage === 'function') { initializeSettingsPage(); } else { console.error('initializeSettingsPage function not found on settings.html'); }")
            elif self.webview_window and current_url and ("loading.html" in current_url or "loading_generated.html" in current_url or "loading_intermediate.html" in current_url):
                 self.logger.info("Loading page has been (re)loaded into the webview.")


    def on_shown(self): # Renamed from _on_shown
        self.logger.debug("Webview 'shown' event fired. Window is visible on screen.")
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
            return f"/* Critical asset {relative_path} is missing. */" if is_critical_fallback else ""
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
        return final_content

    def _execute_js(self, js_code: str):
        if self.webview_window:
            self.webview_window.evaluate_js(js_code)

    def set_status(self, message: str):
        self.logger.info(f"[GUI STATUS] {message}")
        escaped_message = message.replace("\\", "\\\\").replace("'", "\\'")
        self._execute_js(f"if(typeof window.updateStatus === 'function') window.updateStatus('{escaped_message}');")

    def py_toggle_devtools(self):
        if self.webview_window:
            if settings.DEBUG: self.webview_window.toggle_devtools()
            else: self.logger.info("Developer Tools are disabled (DEBUG mode is off).")

    def prepare_and_launch_gui(self, shutdown_event_for_critical_error: Optional[threading.Event] = None):
        try:
            html_content = self._prepare_loading_html()
            if not html_content: raise RuntimeError("Could not prepare HTML for loading page.")
            self.logger.info("🪟 Creating GUI window by loading HTML content directly...")
            self.webview_window = webview.create_window(
                self.app_name, html=html_content, width=self.window_width,
                height=self.window_height, resizable=True
            )
            self.webview_window.events.loaded += self.on_loaded
            self.webview_window.events.shown += self.on_shown
            self.webview_window.events.closing += self._on_closing # Add closing handler

            if settings.DEBUG:
                try: self.webview_window.expose(self.py_toggle_devtools)
                except Exception as e: self.logger.error(f"Failed to expose py_toggle_devtools: {e}")
            self.logger.info("✅ Window created. Events subscribed & functions exposed.")
        except Exception as e:
            self.logger.critical(f"GUI Manager: CRITICAL - Failed to create or launch window: {e}", exc_info=True)
            if shutdown_event_for_critical_error:
                shutdown_event_for_critical_error.set()
            # Re-raise or handle as appropriate, for now, it will propagate up if not caught by main
            raise

    def load_error_page(self, message: str):
        self.logger.error(f"Loading error page with message: {message}")
        error_html_content = self._get_asset_content("error.html")
        if not error_html_content:
            self.logger.error("error.html is missing! Using critical_error.html as fallback.")
            error_html_content = self._get_asset_content("critical_error.html", is_critical_fallback=True)
        
        # Replace placeholder in the error HTML
        if "{ERROR_MESSAGE}" in error_html_content:
            final_html = error_html_content.replace("{ERROR_MESSAGE}", message)
        elif "{MESSAGE}" in error_html_content: # Fallback placeholder
            final_html = error_html_content.replace("{MESSAGE}", message)
        else: # No placeholder found, append the message
            final_html = error_html_content + f"<p>Error: {message}</p>"
            
        if self.webview_window:
            self.webview_window.load_html(final_html)
        else:
            self.logger.error("Cannot load error page: webview_window is None.")

    def load_critical_error_page(self, message: str):
        self.logger.critical(f"Loading critical error page with message: {message}")
        critical_error_html = self._get_asset_content("critical_error.html", is_critical_fallback=True)
        
        if "{MESSAGE}" in critical_error_html:
            final_html = critical_error_html.replace("{MESSAGE}", message)
        else: # No placeholder found, append the message
            final_html = critical_error_html + f"<p>Critical Error: {message}</p>"

        if self.webview_window:
            self.webview_window.load_html(final_html)
        else:
            self.logger.error("Cannot load critical error page: webview_window is None.")


    def redirect_when_ready_loop(self, stop_event: threading.Event,
                                 overall_shutdown_event: threading.Event):
        self.logger.info("Redirect Loop: Started.")
        max_wait_time = 120
        check_interval = 2
        start_time = time.time()

        while not stop_event.is_set() and not overall_shutdown_event.is_set():
            if time.time() - start_time > max_wait_time:
                self.logger.warning("Redirect Loop: Max wait time exceeded for server availability.")
                if not overall_shutdown_event.is_set(): # Avoid changing page if already shutting down
                    self.load_error_page("ComfyUI server did not become available in time. Please check server logs.")
                break

            # Call wait_for_server_availability without the timeout argument
            if self.server_manager.wait_for_server_availability():
                target_url = f"http://{self.connect_host}:{self.port}"
                self.logger.info(f"Redirect Loop: Server is available. Redirecting webview to {target_url}")
                if self.webview_window:
                    self._execute_js("if(typeof window.fadeOutLoading === 'function') window.fadeOutLoading();")
                    time.sleep(1.5) # Give fade out animation time
                    if not overall_shutdown_event.is_set(): # Check again before loading URL
                        self.webview_window.load_url(target_url)
                else:
                    self.logger.error("Redirect Loop: Webview window is not available for redirection.")
                break
            else:
                # Update log message to reflect the actual retry interval
                self.logger.debug(f"Redirect Loop: Server not yet available. Retrying in {check_interval}s...")

            if not self.webview_window or getattr(self.webview_window, 'gui', None) is None:
                self.logger.info("Redirect Loop: Webview window no longer exists. Stopping.")
                break
            # Wait for 'check_interval', breaking if stop_event is set.
            # The main while loop condition handles overall_shutdown_event.
            if stop_event.wait(check_interval):
                self.logger.info("Redirect Loop: stop_event set during wait. Exiting loop.")
                break
        self.logger.info("Redirect Loop: Exiting.")


    def start_webview_blocking(self):
        if self.webview_window:
            self.logger.debug("Starting webview event loop (blocking)...")
            webview.start(debug=settings.DEBUG, private_mode=False, http_server=True)
            self.logger.debug("Webview event loop finished.")
        else:
            self.logger.error("Cannot start webview: window was not created.")
