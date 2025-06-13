import sys
import threading
import time
import logging
from typing import TYPE_CHECKING, Optional
from pathlib import Path # Ensure Path is imported

from .config import settings # Assuming settings is still globally available or passed
from .log_manager import LogManager # Import the new LogManager
from .gui_manager import GUIManager
from . import event_publisher, AppEventType # Import the global event publisher
from .server_manager import ServerManager
from .tray_manager import TrayManager

# Define logger and other global instances, initialized in main()
launcher_logger: logging.Logger = None # type: ignore
gui_manager_instance: Optional[GUIManager] = None
log_manager_instance: Optional[LogManager] = None # Add LogManager instance
server_manager_instance: Optional[ServerManager] = None
tray_manager_instance: Optional[TrayManager] = None
app_logic_thread_instance: Optional[threading.Thread] = None

# Global event to signal application-wide shutdown
app_shutdown_event = threading.Event() # Main shutdown signal
_app_logic_completed_event = threading.Event() # For main to wait for app_logic_thread
_tray_manager_completed_event = threading.Event() # For main to wait for tray_manager_thread


if TYPE_CHECKING:
    from .server_manager import ServerManager as ServerManagerType
    from .gui_manager import GUIManager as GUIManagerType
    from logging import Logger as ActualLoggerType
    # PathType was already defined by importing Path directly

# Define LoggerType for type hinting
if TYPE_CHECKING:
    LoggerType = ActualLoggerType
else:
    LoggerType = logging.Logger

# --- Main Thread Event Handlers (defined at module level) ---
def _handle_main_thread_quit_request():
    if launcher_logger: # Check if logger is initialized
        launcher_logger.info("MainThread Handler: APPLICATION_QUIT_REQUESTED received. Ensuring app_shutdown_event is set.")
    app_shutdown_event.set()

def _handle_critical_error(message: str):
    if launcher_logger:
        launcher_logger.critical(f"MainThread Handler: APPLICATION_CRITICAL_ERROR: {message}")
    if gui_manager_instance: # Check if GUI manager exists to show error
        gui_manager_instance.load_critical_error_page(message)
    app_shutdown_event.set() # Always set shutdown event on critical error

def _handle_server_stopped_unexpectedly(pid: int, returncode: int):
    message = f"ComfyUI server (PID: {pid}) stopped unexpectedly with code {returncode}. Check server.log."
    if launcher_logger:
        launcher_logger.error(f"MainThread Handler: SERVER_STOPPED_UNEXPECTEDLY: {message}")
    if gui_manager_instance and not app_shutdown_event.is_set(): # Avoid changing page if already quitting
        gui_manager_instance.load_error_page(message) # Use non-critical error page
    app_shutdown_event.set() # Ensure main shutdown sequence is triggered

def _handle_app_logic_shutdown_complete():
    if launcher_logger:
        launcher_logger.info("MainThread Handler: APP_LOGIC_SHUTDOWN_COMPLETE received.")
    _app_logic_completed_event.set()
def _handle_tray_manager_shutdown_complete():
    if launcher_logger:
        launcher_logger.info("MainThread Handler: TRAY_MANAGER_SHUTDOWN_COMPLETE received.")
    _tray_manager_completed_event.set()

def custom_excepthook(exc_type, exc_value, exc_traceback):
    global launcher_logger # Use the global logger from this module
    if launcher_logger and launcher_logger.handlers:
        launcher_logger.critical(
            "Unhandled exception caught by custom excepthook:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def app_logic_thread_func(
    app_logger: 'LoggerType',
    gui_manager: 'GUIManagerType',
    current_server_manager: 'ServerManagerType',
    server_log_path: 'Path', # Use Path directly
    shutdown_event_param: threading.Event # Added shutdown event
):
    # Event to signal that GUI content (loading.html) is loaded
    # This replaces waiting directly on gui_manager.is_window_loaded
    _gui_initial_content_loaded_event = threading.Event()

    def _handle_gui_content_loaded():
        app_logger.info("AppLogic Handler: GUI_WINDOW_CONTENT_LOADED received.")
        _gui_initial_content_loaded_event.set()

    event_publisher.subscribe(AppEventType.GUI_WINDOW_CONTENT_LOADED, _handle_gui_content_loaded)
    # No explicit subscription to APPLICATION_QUIT_REQUESTED here, as this thread
    # primarily relies on the shutdown_event_param (global app_shutdown_event)
    # which will be set by TrayManager when it publishes the event.

    app_logger.info("Started.")
    server_process = None
    redirect_thread = None
    redirect_thread_stop_event = threading.Event()

    try:
        app_logger.info("Waiting for GUI window to finish loading initial content (via event)...")
        if not _gui_initial_content_loaded_event.wait(timeout=20):
            app_logger.error("GUI window did not signal 'loaded' in time. Aborting app logic.")
            event_publisher.publish(AppEventType.APPLICATION_CRITICAL_ERROR, message="GUI did not load correctly. Check launcher logs.")
            return
        if shutdown_event_param.is_set(): return

        app_logger.info("GUI content loaded. Proceeding with server launch sequence.")
        gui_manager.set_status("Initializing...")
        if shutdown_event_param.wait(0.5): return

        if shutdown_event_param.is_set(): return
        gui_manager.set_status(f"Clearing network port {settings.PORT}...")
        if not current_server_manager.kill_process_on_port():
            app_logger.warning(f"Failed to kill process on port {settings.PORT}. Server start might fail if port is busy.")
        if shutdown_event_param.wait(0.5): return

        if shutdown_event_param.is_set(): return
        gui_manager.set_status("Starting ComfyUI server process...")
        server_process = current_server_manager.start_server(server_log_path)

        if not server_process:
            app_logger.error("Failed to start ComfyUI server process. Aborting app logic.")
            # Publishing an error event might be more appropriate here if other components need to react
            event_publisher.publish(AppEventType.APPLICATION_CRITICAL_ERROR, message="Could not start the ComfyUI server. Please check the server.log file for details.")
            return
        if shutdown_event_param.is_set(): return

        app_logger.info(f"ComfyUI server process started with PID: {server_process.pid}.")

        redirect_thread = threading.Thread(
            target=gui_manager.redirect_when_ready_loop,
            args=(redirect_thread_stop_event, shutdown_event_param), # Pass stop events
            daemon=True
        )
        redirect_thread.start()
        app_logger.info("Redirection loop initiated.")

        app_logger.info("Now monitoring server process and shutdown event.")
        while not shutdown_event_param.is_set():
            if server_process.poll() is not None:
                app_logger.info(f"ComfyUI server process (PID: {server_process.pid}) has exited with code {server_process.returncode}.")
                # Publish an event indicating unexpected server stop
                if not shutdown_event_param.is_set(): # Only publish if not already shutting down
                    event_publisher.publish(AppEventType.SERVER_STOPPED_UNEXPECTEDLY, pid=server_process.pid, returncode=server_process.returncode)
                    shutdown_event_param.set() # Also trigger local shutdown for this thread
                break
            if shutdown_event_param.wait(timeout=1):
                break

    except Exception as e:
        app_logger.error(f"An error occurred: {e}", exc_info=True)
        if not shutdown_event_param.is_set():
            event_publisher.publish(AppEventType.APPLICATION_CRITICAL_ERROR, message=f"An unexpected error occurred in the background process: {str(e)}")
    finally:
        app_logger.info("Cleaning up...")
        redirect_thread_stop_event.set()

        if redirect_thread and redirect_thread.is_alive():
            app_logger.info("Waiting for redirect thread to join...")
            redirect_thread.join(timeout=3)

        if current_server_manager and server_process and server_process.poll() is None:
            app_logger.info("Shutting down ComfyUI server...")
            current_server_manager.shutdown_server()
        
        # Unsubscribe handlers to prevent issues if this function were somehow called again
        event_publisher.unsubscribe(AppEventType.GUI_WINDOW_CONTENT_LOADED, _handle_gui_content_loaded)
        event_publisher.publish(AppEventType.APP_LOGIC_SHUTDOWN_COMPLETE)
        app_logger.info("Finished.")


def main():
    global launcher_logger, server_manager_instance, tray_manager_instance, gui_manager_instance, log_manager_instance
    global app_logic_thread_instance, app_shutdown_event

    # Ensure module-level events are clear at the start of main,
    # in case of re-entry (e.g., during tests or if main could be called multiple times).
    app_shutdown_event.clear()
    _app_logic_completed_event.clear()
    _tray_manager_completed_event.clear()

    # Initialize LogManager first
    log_manager_instance = LogManager(
        log_dir=settings.LOG_DIR, debug_mode=settings.DEBUG,
        max_files_to_keep_in_archive=settings.MAX_LOG_FILES, max_log_age_days=settings.MAX_LOG_AGE_DAYS
    )
    launcher_logger = log_manager_instance.get_launcher_logger() # Get the configured logger
    sys.excepthook = custom_excepthook

    # Subscribe main thread handlers
    event_publisher.subscribe(AppEventType.APPLICATION_QUIT_REQUESTED, _handle_main_thread_quit_request)
    event_publisher.subscribe(AppEventType.APPLICATION_CRITICAL_ERROR, _handle_critical_error)
    event_publisher.subscribe(AppEventType.SERVER_STOPPED_UNEXPECTEDLY, _handle_server_stopped_unexpectedly)
    event_publisher.subscribe(AppEventType.APP_LOGIC_SHUTDOWN_COMPLETE, _handle_app_logic_shutdown_complete)
    event_publisher.subscribe(AppEventType.TRAY_MANAGER_SHUTDOWN_COMPLETE, _handle_tray_manager_shutdown_complete)

    launcher_logger.info(f"Starting {settings.APP_NAME} (Version 1.0)")
    if settings.DEBUG:
        launcher_logger.debug("Debug mode is ON.")
        launcher_logger.debug(f"Full configuration loaded: {settings.model_dump_json(indent=2)}")

    listen_host_for_comfyui = settings.HOST
    connect_host_for_launcher = settings.EFFECTIVE_CONNECT_HOST
    launcher_logger.info(f"ComfyUI will be instructed to listen on: {listen_host_for_comfyui}:{settings.PORT}")
    launcher_logger.info(f"Launcher will attempt to connect to: {connect_host_for_launcher}:{settings.PORT}")
    server_log_path = settings.LOG_DIR / "server.log"

    try:
        server_manager_instance = ServerManager(
            comfyui_path=settings.COMFYUI_PATH,
            python_executable=settings.PYTHON_EXECUTABLE,
            listen_host=listen_host_for_comfyui,
            connect_host=connect_host_for_launcher,
            port=settings.PORT,
            logger=launcher_logger
        )
        
        gui_manager_instance = GUIManager(
            app_name=settings.APP_NAME,
            window_width=settings.WINDOW_WIDTH,
            window_height=settings.WINDOW_HEIGHT,
            connect_host=connect_host_for_launcher,
            port=settings.PORT,
            assets_dir=settings.ASSETS_DIR,
            logger=launcher_logger,
            server_manager=server_manager_instance
        )
        
        tray_manager_instance = TrayManager(
            app_name=settings.APP_NAME,
            assets_dir=settings.ASSETS_DIR,
            logger=launcher_logger,
            shutdown_event=app_shutdown_event, # Pass the event
            gui_manager=gui_manager_instance  # Pass gui_manager
        )
        
        gui_manager_instance.prepare_and_launch_gui(shutdown_event_for_critical_error=app_shutdown_event)
        
        # Set the log path in the React app once it's loaded
        def set_log_path_when_ready():
            gui_manager_instance.is_window_loaded.wait(timeout=10)  # Wait up to 10 seconds
            if gui_manager_instance.is_window_loaded.is_set():
                gui_manager_instance.set_log_path(str(server_log_path))
        
        # Start thread to set log path
        threading.Thread(target=set_log_path_when_ready, daemon=True).start()
        
        tray_manager_instance.start()

        app_logic_thread_instance = threading.Thread(
            target=app_logic_thread_func,
            args=(launcher_logger, gui_manager_instance, server_manager_instance, server_log_path, app_shutdown_event),
            daemon=True # Daemon so it exits if main thread exits unexpectedly
        )
        app_logic_thread_instance.start()
        launcher_logger.info(f"{settings.APP_NAME} setup complete. GUI, Tray, and Background thread launched.")

        launcher_logger.info("Entering blocking call gui_manager_instance.start_webview_blocking()...")
        # This call is blocking. It will return when webview.destroy_window() is called
        # or if the window is closed and _on_closing doesn't prevent it (which it now does).
        gui_manager_instance.start_webview_blocking()
        launcher_logger.info("Returned from gui_manager_instance.start_webview_blocking().")

        # If start_webview_blocking returns, it means the window was either closed by user
        # (and our _on_closing hid it), or webview.destroy_window() was called.
        # The application should now wait for the app_shutdown_event to be set (e.g., by the tray's Quit).
        launcher_logger.info("Webview blocking call has returned. Waiting for application shutdown signal.")
        app_shutdown_event.wait() # Wait indefinitely; quit is now signaled by event handlers setting this
        launcher_logger.info("Application shutdown signal received.")

    except Exception as e:
        launcher_logger.critical(f"An unhandled exception occurred: {e}", exc_info=True)
        app_shutdown_event.set() # Ensure shutdown is signaled
    finally:
        launcher_logger.info("Initiating shutdown sequence (finally block)...")
        # Ensure app_shutdown_event is set, though it should be by now if quit was graceful.
        # If an exception occurred before APPLICATION_QUIT_REQUESTED was handled, this ensures it's set.
        if not app_shutdown_event.is_set():
            app_shutdown_event.set()

        launcher_logger.info("Checking app logic thread...")
        if not _app_logic_completed_event.wait(timeout=12): # Increased timeout slightly
            launcher_logger.info("Waiting for app logic thread to complete...")
            if app_logic_thread_instance and app_logic_thread_instance.is_alive(): # Check if thread object exists and is alive
                launcher_logger.warning("App logic thread did not signal completion and is still alive.")
            elif not app_logic_thread_instance:
                 launcher_logger.warning("App logic thread instance is None, cannot confirm completion status.")
        else:
            launcher_logger.info("App logic thread signaled completion or timed out.")

        # Server shutdown is primarily handled by app_logic_thread_func.
        # Final check here.
        launcher_logger.info("Checking server manager for final shutdown...")
        if server_manager_instance and getattr(server_manager_instance, 'server_process', None) and \
           server_manager_instance.server_process.poll() is None:
            launcher_logger.info("Performing final check/attempt to shut down ComfyUI server...")
            server_manager_instance.shutdown_server()
        else:
            launcher_logger.info("Server manager or server process not active for final shutdown.")

        # TrayManager's icon.stop() is handled by its own APPLICATION_QUIT_REQUESTED handler.
        # We wait for the TRAY_MANAGER_SHUTDOWN_COMPLETE event which is published when its run() loop finishes.
        launcher_logger.info("Checking TrayManager thread...")
        if not _tray_manager_completed_event.wait(timeout=5):
            launcher_logger.info("Waiting for TrayManager thread to complete...")
            if tray_manager_instance and tray_manager_instance._thread and tray_manager_instance._thread.is_alive():
                launcher_logger.warning("TrayManager thread did not signal completion and is still alive.")
        else:
            launcher_logger.info("TrayManager thread signaled completion or timed out.")
        launcher_logger.info("Checking GUI manager for window destroy...")
        if gui_manager_instance and gui_manager_instance.webview_window:
            launcher_logger.info("Destroying GUI window (final step)...")
            # Call destroy() directly on the window instance
            # This might be redundant if TrayManager already destroyed it, but should be safe.
            try:
                gui_manager_instance.webview_window.destroy()
                launcher_logger.info("MAIN THREAD: GUI window destroy command sent (final step).")
            except Exception as e: # pywebview might raise if already destroyed or other issues
                launcher_logger.warning(f"MAIN THREAD: Error destroying GUI window (final step, might be already destroyed): {e}")
        else:
            launcher_logger.info("GUI manager or webview window not active for destroy.")

        # Unsubscribe main thread handlers
        event_publisher.unsubscribe(AppEventType.APPLICATION_QUIT_REQUESTED, _handle_main_thread_quit_request)
        event_publisher.unsubscribe(AppEventType.APPLICATION_CRITICAL_ERROR, _handle_critical_error)
        event_publisher.unsubscribe(AppEventType.SERVER_STOPPED_UNEXPECTEDLY, _handle_server_stopped_unexpectedly)
        event_publisher.unsubscribe(AppEventType.APP_LOGIC_SHUTDOWN_COMPLETE, _handle_app_logic_shutdown_complete)
        event_publisher.unsubscribe(AppEventType.TRAY_MANAGER_SHUTDOWN_COMPLETE, _handle_tray_manager_shutdown_complete)

        launcher_logger.info(f"{settings.APP_NAME} has exited cleanly.")
        logging.shutdown() # Ensure all log handlers are flushed


if __name__ == "__main__":
    # The main launcher_logger is set up early in main() now, handling console output.
    try:
        main()
    except Exception as e:
        # The custom_excepthook should have logged this if launcher_logger was set.
        # This is a last resort.
        print(f"FATAL PRE-MAIN ERROR (should have been caught by excepthook): {e}", file=sys.__stderr__)
        import traceback
        traceback.print_exception(e, file=sys.__stderr__)
    # logging.shutdown() is now called at the end of main's finally block
