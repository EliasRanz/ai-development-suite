import sys
import threading
import time
import logging
from typing import TYPE_CHECKING, Optional # Added Optional
# Removed signal import as it's handled in server_manager

from .config import settings
from .logger_setup import setup_launcher_logger, rotate_and_cleanup_logs
from .gui_manager import GUIManager
from .server_manager import ServerManager

# Define logger and server_manager_instance at module level,
# but they will be initialized/assigned within main() or by main().
logger: logging.Logger = None # type: ignore
server_manager_instance: Optional[ServerManager] = None # To hold the server_manager instance for shutdown

if TYPE_CHECKING:
    from .server_manager import ServerManager as ServerManagerType
    from .gui_manager import GUIManager as GUIManagerType
    # Corrected LoggerType to avoid conflict with the 'logger' variable
    from logging import Logger as ActualLoggerType
    from pathlib import Path as PathType

# Define LoggerType for type hinting after potential import conflicts are resolved
if TYPE_CHECKING:
    LoggerType = ActualLoggerType
else:
    LoggerType = logging.Logger


def custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to log unhandled exceptions."""
    # The 'logger' variable here refers to the global 'logger' from __main__.py's scope.
    # It's crucial that this hook is set *after* the main logger is configured.
    if logger and logger.handlers: # Check if our main logger is configured
        logger.critical(
            "Unhandled exception caught by custom excepthook:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    else:
        # Fallback if our main logger isn't set up (e.g., error before logger init)
        # or if the hook was somehow called when logger was None.
        # This will print to stderr if available, or be lost in a noconsole app.
        sys.__excepthook__(exc_type, exc_value, exc_traceback) # Call the original hook


def app_logic_thread_func(
    app_logger: 'LoggerType',
    gui_manager: 'GUIManagerType',
    current_server_manager: 'ServerManagerType',
    server_log_path: 'PathType'
):
    """
    Handles the application logic after the GUI object is created.
    This function runs in a separate thread.
    """
    app_logger.info("BACKGROUND THREAD: Started.")
    app_logger.info("BACKGROUND THREAD: Waiting for GUI window to finish loading content...")
    # Wait for the GUI window to signal it has loaded its initial content
    is_gui_content_ready = gui_manager.is_window_loaded.wait(timeout=20) # Default 20s timeout

    if not is_gui_content_ready:
        app_logger.error("BACKGROUND THREAD: GUI window did not signal 'loaded' in time. Aborting app logic.")
        # Attempt to show an error in the GUI, though it might not be fully responsive
        if gui_manager.webview_window:
            try:
                # Try to load a more specific critical error page if available
                critical_error_html = gui_manager._get_asset_content("critical_error.html", is_critical_fallback=True)
                if "{MESSAGE}" in critical_error_html:
                    critical_error_html = critical_error_html.replace("{MESSAGE}", "GUI did not load correctly. Check launcher logs.")
                gui_manager.webview_window.load_html(critical_error_html)
            except Exception as e_gui:
                app_logger.error(f"BACKGROUND_THREAD: Failed to display critical error in GUI: {e_gui}")
        return

    app_logger.info("BACKGROUND THREAD: GUI content loaded. Proceeding with server launch sequence.")
    gui_manager.set_status("Initializing...")
    time.sleep(0.5)

    gui_manager.set_status(f"Clearing network port {settings.PORT}...")
    current_server_manager.kill_process_on_port()
    time.sleep(0.5)

    gui_manager.set_status("Starting ComfyUI server process...")
    # ServerManager now stores the process internally
    server_process_obj = current_server_manager.start_server(server_log_path)

    if not server_process_obj:
        gui_manager.set_status("Fatal Error: Could not start server.")
        app_logger.error("BACKGROUND THREAD: Failed to start ComfyUI server process. Aborting app logic.")
        if gui_manager.webview_window:
            try:
                error_html = gui_manager._get_asset_content("error.html", is_critical_fallback=True)
                if "{ERROR_MESSAGE}" in error_html: # Assuming error.html might have a placeholder
                    error_html = error_html.replace("{ERROR_MESSAGE}", "Could not start the ComfyUI server. Please check the server.log file for details.")
                elif "{MESSAGE}" in error_html: # Fallback placeholder
                     error_html = error_html.replace("{MESSAGE}", "Could not start the ComfyUI server. Please check the server.log file for details.")
                gui_manager.webview_window.load_html(error_html)
            except Exception as e_gui:
                app_logger.error(f"BACKGROUND_THREAD: Failed to display server start error in GUI: {e_gui}")
        return

    # Start the redirection logic (which also runs in its own thread from within GUIManager)
    # Pass the current_server_manager instance to redirect_when_ready_loop if it needs it
    # For now, assuming redirect_when_ready_loop uses the server_manager passed to GUIManager's init
    threading.Thread(target=gui_manager.redirect_when_ready_loop, daemon=True).start()
    app_logger.info("BACKGROUND THREAD: Redirection loop initiated.")
    app_logger.info("BACKGROUND THREAD: Finished its primary tasks.")


def main():
    global logger, server_manager_instance # Declare we're modifying the globals

    # --- Logger and Initial Setup moved inside main() ---
    rotate_and_cleanup_logs(settings.LOG_DIR, settings.MAX_LOG_FILES, settings.MAX_LOG_AGE_DAYS)
    # Assign to global logger
    logger = setup_launcher_logger(settings.LOG_DIR, settings.DEBUG)

    # Set the global exception hook AFTER the main logger is configured
    sys.excepthook = custom_excepthook

    logger.info(f"Starting {settings.APP_NAME} (Version 1.0)")
    if settings.DEBUG:
        logger.debug("Debug mode is ON.")
        # Log all settings if in debug mode for easier troubleshooting
        logger.debug(f"Full configuration loaded: {settings.model_dump_json(indent=2)}")
    
    # Determine listen and connect hosts
    listen_host_for_comfyui = settings.HOST
    connect_host_for_launcher = settings.EFFECTIVE_CONNECT_HOST

    logger.info(f"ComfyUI will be instructed to listen on: {listen_host_for_comfyui}:{settings.PORT}")
    logger.info(f"Launcher will attempt to connect to: {connect_host_for_launcher}:{settings.PORT}")

    server_log_path = settings.LOG_DIR / "server.log"

    # Instantiate managers
    current_server_manager = ServerManager(
        comfyui_path=settings.COMFYUI_PATH,
        python_executable=settings.PYTHON_EXECUTABLE,
        listen_host=listen_host_for_comfyui,
        connect_host=connect_host_for_launcher,
        port=settings.PORT,
        logger=logger
    )
    server_manager_instance = current_server_manager # Store for shutdown access
    gui_manager = GUIManager(
        app_name=settings.APP_NAME,
        window_width=settings.WINDOW_WIDTH,
        window_height=settings.WINDOW_HEIGHT,
        connect_host=connect_host_for_launcher, # GUIManager uses this for webview.load_url
        port=settings.PORT,
        assets_dir=settings.ASSETS_DIR,
        logger=logger,
        server_manager=current_server_manager # Pass the instance
    )

    # --- Main Thread Logic ---
    try:
        # This creates the window object, prepares HTML, and subscribes events
        gui_manager.prepare_and_launch_gui()
    except Exception as e:
        logger.error(f"MAIN THREAD: A critical error occurred while preparing the GUI: {e}", exc_info=True)
        # Attempt to show a very basic error if GUI preparation itself fails catastrophically
        # This is a last resort as the GUI manager might be in an unusable state.
        try:
            import webview
            webview.create_window("Launcher Critical Error", html="<h1>Launcher Critical Error</h1><p>Failed to initialize GUI. Check logs.</p>", width=600, height=200)
            webview.start()
        except Exception as fallback_e:
            logger.error(f"MAIN THREAD: Fallback GUI error display also failed: {fallback_e}")
        return

    # Start the background thread to handle server startup and subsequent GUI updates
    app_logic_thread = threading.Thread(
        target=app_logic_thread_func,
        args=(logger, gui_manager, current_server_manager, server_log_path),
        daemon=True # Daemon threads exit when the main program exits
    )
    app_logic_thread.start()
    logger.info("MAIN THREAD: Background application logic thread started.")

    # Now, call the blocking webview.start() on the main thread.
    # This is done much sooner to allow pywebview's event loop to run.
    logger.info("MAIN THREAD: Starting webview event loop (this will block)...")
    gui_manager.start_webview_blocking() # This calls webview.start(debug=settings.DEBUG)

    # --- Shutdown Sequence (after webview window is closed by the user) ---
    logger.info("MAIN THREAD: GUI window closed. Initiating shutdown...")

    if server_manager_instance:
        server_manager_instance.shutdown_server() # ServerManager handles its own process
        logger.info("MAIN THREAD: ComfyUI server shutdown sequence complete.")
    else:
        logger.warning("MAIN THREAD: ServerManager instance not found; skipping server shutdown.")

    if app_logic_thread.is_alive():
        logger.info("MAIN THREAD: Waiting for background application logic thread to complete...")
        app_logic_thread.join(timeout=5) # Give it a few seconds to finish
        if app_logic_thread.is_alive():
            logger.warning("MAIN THREAD: Background application logic thread did not complete cleanly after timeout.")

    logger.info(f"MAIN THREAD: {settings.APP_NAME} has exited cleanly.")


if __name__ == "__main__":
    # Initialize a placeholder logger for pre-main errors if main_logger isn't set yet
    # This is unlikely to be used if main() sets up the logger correctly.
    main_logger = logging.getLogger("ComfyUILauncher_PreMain")
    if not main_logger.hasHandlers():
        pre_main_handler = logging.StreamHandler(sys.stdout)
        pre_main_formatter = logging.Formatter("[%(asctime)s] [PRE-MAIN] %(message)s", datefmt="%H:%M:%S")
        pre_main_handler.setFormatter(pre_main_formatter)
        main_logger.addHandler(pre_main_handler)
        main_logger.setLevel(logging.INFO)

    try:
        main()
    except Exception as e:
        # If an exception reaches here, sys.excepthook should have already handled it
        # if 'logger' was set. If 'logger' wasn't set, this is a very early error.
        # The custom_excepthook will attempt to log it.
        # We can add a print to original stderr as a last resort if the packager allows.
        print(f"FATAL PRE-MAIN ERROR (should have been caught by excepthook): {e}", file=sys.__stderr__)
        import traceback
        traceback.print_exception(e, file=sys.__stderr__)
    finally:
        # Ensure logging.shutdown() is called to flush handlers
        # Use the globally set 'logger' if available for a final message
        effective_logger = logger if logger and logger.handlers else main_logger
        effective_logger.info("Calling logging.shutdown()...")
        logging.shutdown()
