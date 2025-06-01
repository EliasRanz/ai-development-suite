import sys
import threading
import time
import logging
from typing import TYPE_CHECKING, Optional
from pathlib import Path # Ensure Path is imported

from .config import settings
from .logger_setup import setup_launcher_logger, rotate_and_cleanup_logs
from .gui_manager import GUIManager
from .server_manager import ServerManager
from .tray_manager import TrayManager

# Define logger and other global instances, initialized in main()
launcher_logger: logging.Logger = None # type: ignore
gui_manager_instance: Optional[GUIManager] = None
server_manager_instance: Optional[ServerManager] = None
tray_manager_instance: Optional[TrayManager] = None
app_logic_thread_instance: Optional[threading.Thread] = None

# Global event to signal application-wide shutdown
app_shutdown_event = threading.Event()


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
    app_logger.info("BACKGROUND THREAD: Started.")
    server_process = None
    redirect_thread = None
    redirect_thread_stop_event = threading.Event()

    try:
        app_logger.info("BACKGROUND THREAD: Waiting for GUI window to finish loading content...")
        if not gui_manager.is_window_loaded.wait(timeout=20):
            app_logger.error("BACKGROUND THREAD: GUI window did not signal 'loaded' in time. Aborting app logic.")
            if not shutdown_event_param.is_set():
                gui_manager.load_critical_error_page("GUI did not load correctly. Check launcher logs.")
            shutdown_event_param.set()
            return
        if shutdown_event_param.is_set(): return

        app_logger.info("BACKGROUND THREAD: GUI content loaded. Proceeding with server launch sequence.")
        gui_manager.set_status("Initializing...")
        if shutdown_event_param.wait(0.5): return

        if shutdown_event_param.is_set(): return
        gui_manager.set_status(f"Clearing network port {settings.PORT}...")
        if not current_server_manager.kill_process_on_port():
            app_logger.warning(f"BACKGROUND THREAD: Failed to kill process on port {settings.PORT}. Server start might fail if port is busy.")
        if shutdown_event_param.wait(0.5): return

        if shutdown_event_param.is_set(): return
        gui_manager.set_status("Starting ComfyUI server process...")
        server_process = current_server_manager.start_server(server_log_path)

        if not server_process:
            app_logger.error("BACKGROUND THREAD: Failed to start ComfyUI server process. Aborting app logic.")
            if not shutdown_event_param.is_set():
                gui_manager.load_error_page("Could not start the ComfyUI server. Please check the server.log file for details.")
            shutdown_event_param.set()
            return
        if shutdown_event_param.is_set(): return

        app_logger.info(f"BACKGROUND THREAD: ComfyUI server process started with PID: {server_process.pid}.")

        redirect_thread = threading.Thread(
            target=gui_manager.redirect_when_ready_loop,
            args=(redirect_thread_stop_event, shutdown_event_param), # Pass stop events
            daemon=True
        )
        redirect_thread.start()
        app_logger.info("BACKGROUND THREAD: Redirection loop initiated.")

        app_logger.info("BACKGROUND THREAD: Now monitoring server process and shutdown event.")
        while not shutdown_event_param.is_set():
            if server_process.poll() is not None:
                app_logger.info(f"BACKGROUND THREAD: ComfyUI server process (PID: {server_process.pid}) has exited with code {server_process.returncode}.")
                if not shutdown_event_param.is_set():
                    gui_manager.load_error_page(f"ComfyUI server (PID: {server_process.pid}) stopped unexpectedly. Check server.log.")
                shutdown_event_param.set()
                break
            if shutdown_event_param.wait(timeout=1):
                break

    except Exception as e:
        app_logger.error(f"BACKGROUND THREAD: An error occurred: {e}", exc_info=True)
        if not shutdown_event_param.is_set():
            gui_manager.load_critical_error_page(f"An unexpected error occurred in the background process: {str(e)}")
        shutdown_event_param.set()
    finally:
        app_logger.info("BACKGROUND THREAD: Cleaning up...")
        redirect_thread_stop_event.set()

        if redirect_thread and redirect_thread.is_alive():
            app_logger.info("BACKGROUND THREAD: Waiting for redirect thread to join...")
            redirect_thread.join(timeout=3)

        if current_server_manager and server_process and server_process.poll() is None:
            app_logger.info("BACKGROUND THREAD: Shutting down ComfyUI server...")
            current_server_manager.shutdown_server()
        app_logger.info("BACKGROUND THREAD: Finished.")


def main():
    global launcher_logger, server_manager_instance, tray_manager_instance, gui_manager_instance
    global app_logic_thread_instance, app_shutdown_event

    rotate_and_cleanup_logs(settings.LOG_DIR, settings.MAX_LOG_FILES, settings.MAX_LOG_AGE_DAYS)
    launcher_logger = setup_launcher_logger(settings.LOG_DIR, settings.DEBUG)
    sys.excepthook = custom_excepthook

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
        tray_manager_instance.start()

        app_logic_thread_instance = threading.Thread(
            target=app_logic_thread_func,
            args=(launcher_logger, gui_manager_instance, server_manager_instance, server_log_path, app_shutdown_event),
            daemon=True # Daemon so it exits if main thread exits unexpectedly
        )
        app_logic_thread_instance.start()
        launcher_logger.info(f"MAIN THREAD: {settings.APP_NAME} setup complete. GUI, Tray, and Background thread launched.")

        # This call is blocking. It will return when webview.destroy_window() is called
        # or if the window is closed and _on_closing doesn't prevent it (which it now does).
        gui_manager_instance.start_webview_blocking()

        # If start_webview_blocking returns, it means the window was either closed by user
        # (and our _on_closing hid it), or webview.destroy_window() was called.
        # The application should now wait for the app_shutdown_event to be set (e.g., by the tray's Quit).
        launcher_logger.info("MAIN THREAD: Webview blocking call has returned. Waiting for application shutdown signal.")
        app_shutdown_event.wait() # Wait for tray "Quit" or other shutdown signal
        launcher_logger.info("MAIN THREAD: Application shutdown signal received.")

    except Exception as e:
        launcher_logger.critical(f"MAIN THREAD: An unhandled exception occurred: {e}", exc_info=True)
        app_shutdown_event.set() # Ensure shutdown is signaled
    finally:
        launcher_logger.info("MAIN THREAD: Initiating shutdown sequence...")
        app_shutdown_event.set() # Ensure event is set for all components

        if app_logic_thread_instance and app_logic_thread_instance.is_alive():
            launcher_logger.info("MAIN THREAD: Waiting for app logic thread to complete...")
            app_logic_thread_instance.join(timeout=10)
            if app_logic_thread_instance.is_alive():
                launcher_logger.warning("MAIN THREAD: App logic thread did not exit cleanly after 10s.")

        # Server shutdown is primarily handled by app_logic_thread_func.
        # Final check here.
        if server_manager_instance and getattr(server_manager_instance, 'server_process', None) and \
           server_manager_instance.server_process.poll() is None:
            launcher_logger.info("MAIN THREAD: Performing final check/attempt to shut down ComfyUI server...")
            server_manager_instance.shutdown_server()

        if tray_manager_instance:
            launcher_logger.info("MAIN THREAD: Stopping tray manager...")
            tray_manager_instance.stop()

        if gui_manager_instance and gui_manager_instance.webview_window:
            launcher_logger.info("MAIN THREAD: Destroying GUI window...")
            # Call destroy() directly on the window instance
            gui_manager_instance.webview_window.destroy()

        launcher_logger.info(f"MAIN THREAD: {settings.APP_NAME} has exited cleanly.")
        logging.shutdown() # Ensure all log handlers are flushed


if __name__ == "__main__":
    main_logger_pre = logging.getLogger("ComfyUILauncher_PreMain") # Renamed to avoid conflict
    if not main_logger_pre.hasHandlers():
        pre_main_handler = logging.StreamHandler(sys.stdout)
        pre_main_formatter = logging.Formatter("[%(asctime)s] [PRE-MAIN] %(message)s", datefmt="%H:%M:%S")
        pre_main_handler.setFormatter(pre_main_formatter)
        main_logger_pre.addHandler(pre_main_handler)
        main_logger_pre.setLevel(logging.INFO)

    try:
        main()
    except Exception as e:
        # The custom_excepthook should have logged this if launcher_logger was set.
        # This is a last resort.
        print(f"FATAL PRE-MAIN ERROR (should have been caught by excepthook): {e}", file=sys.__stderr__)
        import traceback
        traceback.print_exception(e, file=sys.__stderr__)
    # logging.shutdown() is now called at the end of main's finally block
