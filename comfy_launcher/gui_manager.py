import webview
import threading
import time
from pathlib import Path
import os
import platform # For checking the OS
import subprocess # For calling external commands (macOS/Linux theme detection)
from typing import Literal # For type hinting the theme preference

# Conditionally import winreg only on Windows
if platform.system() == "Windows":
    import winreg
else:
    winreg = None # Define winreg as None on non-Windows systems

from .config import settings

class GUIManager:
    def __init__(self, app_name: str, window_width: int, window_height: int,
                 host: str, port: int, assets_dir: Path, logger, server_manager):
        self.app_name = app_name
        self.window_width = window_width
        self.window_height = window_height
        self.host = host
        self.port = port
        self.assets_dir = assets_dir
        self.logger = logger
        self.server_manager = server_manager
        self.webview_window = None
        self._loading_html_path = None 
        self.is_window_loaded = threading.Event()
        self.is_window_shown = threading.Event()

    def on_loaded(self):
        self.logger.info("🎉 Webview 'on_loaded' event fired!")
        current_url = self.webview_window.get_current_url() if self.webview_window else "N/A"
        self.logger.debug(f"Current URL in webview at on_loaded: {current_url}")

        if not self.is_window_loaded.is_set():
            self.logger.debug("Signaling main thread that window is loaded for the first time.")
            self.is_window_loaded.set()
        else:
            self.logger.debug("Webview 'loaded' event fired again (e.g., after page navigation).")
            # This logic was for a settings page that was scrapped.
            # It can be removed or kept if you plan to add navigation later.
            # For now, the test expects the log message if settings.html is "loaded".
            if self.webview_window: 
                if current_url and "settings.html" in current_url: 
                     self.logger.info("Settings page has been loaded into the webview.")
                     self._execute_js("if (typeof initializeSettingsPage === 'function') { initializeSettingsPage(); } else { console.error('initializeSettingsPage function not found on settings.html'); }")
                elif current_url and ("loading.html" in current_url or "loading_generated.html" in current_url or "loading_intermediate.html" in current_url):
                     self.logger.info("Loading page has been (re)loaded into the webview.")

    def on_shown(self):
        self.logger.debug("Webview 'shown' event fired. Window is visible on screen.")
        if not self.is_window_shown.is_set():
          self.is_window_shown.set()

    def _get_system_theme_preference(self) -> Literal["dark", "light"]:
        """
        Tries to determine the system's preferred color scheme (dark or light).
        Defaults to "light" if detection fails or is not implemented for the OS.
        """
        system_os = platform.system()
        theme: Literal["dark", "light"] = "light" # Default theme

        if system_os == "Windows":
            if winreg: # winreg is already conditionally imported
                try:
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    if value == 0: # AppsUseLightTheme is 0 for dark mode
                        theme = "dark"
                except Exception:
                    self.logger.debug("Could not determine Windows dark mode via registry, using default.", exc_info=True)
            else:
                self.logger.debug("winreg module not available for Windows theme detection, using default theme.")

        elif system_os == "Darwin": # macOS
            try:
                cmd = ["defaults", "read", "-g", "AppleInterfaceStyle"]
                process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=2)
                if process.returncode == 0 and process.stdout.strip() == "Dark":
                    theme = "dark"
                self.logger.debug(f"macOS theme detection via 'defaults': stdout='{process.stdout.strip()}', theme='{theme}'")
            except FileNotFoundError:
                self.logger.warning("'defaults' command not found for macOS theme detection. Using default theme.")
            except subprocess.TimeoutExpired:
                self.logger.warning("macOS theme detection via 'defaults' timed out. Using default theme.")
            except Exception as e:
                self.logger.error(f"Error detecting macOS theme: {e}. Using default theme.", exc_info=True)

        elif system_os == "Linux":
            try: # Try XDG Desktop Portal first
                cmd_xdg = [
                    "gdbus", "call", "--session",
                    "--dest", "org.freedesktop.portal.Desktop",
                    "--object-path", "/org/freedesktop/portal/desktop",
                    "--method", "org.freedesktop.portal.Settings.Read",
                    "org.freedesktop.appearance", "color-scheme"
                ]
                process_xdg = subprocess.run(cmd_xdg, capture_output=True, text=True, check=True, timeout=2)
                output_xdg = process_xdg.stdout.strip().lower()
                if "'color-scheme': <uint32 1>" in output_xdg: # 1 means prefer-dark
                    theme = "dark"
                elif "'color-scheme': <uint32 2>" in output_xdg: # 2 means prefer-light
                    theme = "light"
                self.logger.debug(f"Linux XDG portal theme detection: output='{output_xdg}', theme='{theme}'")
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e_xdg:
                self.logger.info(f"XDG Portal method for Linux theme detection failed: {e_xdg}. Using default theme.")
            except Exception as e_linux: # Catch any other unexpected error
                self.logger.error(f"Unexpected error during Linux XDG theme detection: {e_linux}. Using default theme.", exc_info=True)
        else:
            self.logger.info(f"System theme detection not implemented for OS '{system_os}'. Using default theme.")

        self.logger.info(f"Determined system theme preference: '{theme}' for OS '{system_os}'.")
        return theme

    def _get_asset_content(self, relative_path: str, is_critical_fallback: bool = False) -> str:
        asset_path = self.assets_dir / relative_path
        try:
            with open(asset_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"Asset file not found: {asset_path}")
            return f"/* Critical asset {relative_path} is missing. */" if is_critical_fallback else ""
        except Exception as e:
            self.logger.exception(f"Error reading asset file {asset_path}: {e}")
            return ""

    def _prepare_loading_html(self):
        self.logger.debug("Preparing full HTML structure with minimal CSS and inlined JS...")
        html_template_content = self._get_asset_content("loading_base.html")
        if not html_template_content:
            # If loading_base.html is missing, try fallback_loading.html
            self.logger.error("loading_base.html is missing. Attempting to use fallback_loading.html.")
            html_template_content = self._get_asset_content("fallback_loading.html", is_critical_fallback=True)
            if not html_template_content: # If fallback also fails
                 raise FileNotFoundError("Both loading_base.html and fallback_loading.html could not be read.")


        js_content = self._get_asset_content("loading.js")
        if not js_content:
            self.logger.warning("loading.js could not be loaded! Using fallback JS.")
            js_content = """
            window.updateStatus = function(msg) { console.log('Fallback updateStatus:', msg); };
            window.setLogPath = function(path) { console.log('Fallback setLogPath:', path); };
            window.fadeOutLoading = function() { console.log('Fallback fadeOutLoading'); };
            """
        
        # Using the minimal CSS strategy that we know works
        minimal_css_content = """
        body { margin: 0; padding: 20px; box-sizing: border-box; background-color: #1a1a1a; color: #f0f0f0; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; }
        .container { padding: 40px; background-color: #242424; border-radius: 8px; max-width: 500px; }
        .title { font-size: 1.8em; margin-bottom: 15px; } .accent { color: #0099ff; }
        #status-message { margin-top: 15px; color: #aaa; min-height: 1.2em; }        
        .spinner { width: 50px; height: 50px; border: 5px solid #555; border-top-color: #0099ff; border-radius: 50%; margin: 0 auto 20px auto; animation: spin_simple 1.2s linear infinite; }
        @keyframes spin_simple { to { transform: rotate(360deg); } }
        #loader-wrapper { opacity: 1; } .fade-out { opacity: 0; transition: opacity 0.5s ease-out; }
        """
        content_with_css = html_template_content.replace("{CSS_CONTENT}", minimal_css_content)
        content_with_js = content_with_css.replace("{JS_CONTENT}", js_content)
        
        if settings.LAUNCHER_THEME == "dark":
            theme_class = "dark"
        elif settings.LAUNCHER_THEME == "light":
            theme_class = "light"
        else: # "system" or any unexpected value defaults to system detection
            theme_class = self._get_system_theme_preference()
            
        final_content = content_with_js.replace("{THEME_CLASS}", theme_class)
            
        # This generated file is mostly for debugging the composed HTML if needed.
        # The application loads the 'final_content' string directly.
        self._loading_html_path = self.assets_dir.parent / "loading_generated.html" 
        try:
            with open(self._loading_html_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            self.logger.debug(f"Generated loading HTML written to: {self._loading_html_path}")
        except Exception as e:
            self.logger.warning(f"Could not write generated loading HTML: {e}")
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
            if settings.DEBUG:
                self.logger.info("Toggling Developer Tools via F12...")
                self.webview_window.toggle_devtools()
            else:
                self.logger.info("Developer Tools are disabled (DEBUG mode is off).")

    def prepare_and_launch_gui(self):
        html_content = self._prepare_loading_html()
        if not html_content:
            raise RuntimeError("Could not prepare the HTML content for the loading page.")
        
        self.logger.info("🪟 Creating GUI window by loading HTML content directly...")
        self.webview_window = webview.create_window(
            self.app_name,
            html=html_content,
            width=self.window_width,
            height=self.window_height,
            resizable=True
        )
        self.webview_window.events.loaded += self.on_loaded
        self.webview_window.events.shown += self.on_shown
        
        if settings.DEBUG: # Only expose devtools toggle if in debug mode
            try:
                self.webview_window.expose(self.py_toggle_devtools)
                self.logger.debug("py_toggle_devtools function exposed to JavaScript.")
            except Exception as e:
                 self.logger.error(f"Failed to expose py_toggle_devtools: {e}")
        # No other functions are exposed as settings UI was scrapped
        self.logger.info("✅ Window created. Events subscribed & functions exposed.")

    def redirect_when_ready_loop(self):
        if not self.webview_window:
            self.logger.error("Cannot redirect: Webview window not initialized.")
            return
        try:
            self.set_status(f"Waiting for server on port {self.port}...")
            if self.server_manager.wait_for_server_availability():
                self.set_status("Server found! Preparing interface...")
                self.logger.info("🌐 ComfyUI is available, switching GUI...")
                self._execute_js("if(typeof window.fadeOutLoading === 'function') window.fadeOutLoading();")
                time.sleep(1.5)
                self.webview_window.load_url(f"http://{self.host}:{self.port}")
                self.logger.info("🪄 Switched to ComfyUI interface.")
            else:
                self.set_status("Error: Server did not respond.")
                self.logger.error("❌ ComfyUI server never became available. Displaying error page.")
                error_html_content = self._get_asset_content("error.html") 
                if not error_html_content : 
                    self.logger.error("error.html is missing or unreadable! Displaying critical error.")
                    error_html_content = self._get_asset_content("critical_error.html", is_critical_fallback=True)
                self.webview_window.load_html(error_html_content)
        except Exception as e:
            self.logger.exception(f"🛑 An error occurred in the redirection thread: {e}")

    def start_webview_blocking(self):
        if self.webview_window:
            self.logger.debug("Starting webview event loop...")
            webview.start(debug=settings.DEBUG) # Let pywebview choose the best GUI backend
            self.logger.debug("Webview event loop finished.")
        else:
            self.logger.error("Cannot start webview: window was not created.")
