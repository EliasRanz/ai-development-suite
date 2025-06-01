import subprocess
import signal
import time
import psutil # type: ignore
import socket
from pathlib import Path
import platform
import os # For os.kill / os.killpg
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger # For type hinting

class ServerManager:
    def __init__(self, comfyui_path: Path, python_executable: Path,
                 host: str, port: int, logger: 'Logger'):
        self.comfyui_path = comfyui_path
        self.python_executable = python_executable
        self.host = host
        self.port = port
        self.logger = logger
        self.server_process: Optional[subprocess.Popen] = None # Store the managed process

    def kill_process_on_port(self):
        self.logger.debug(f"Checking for processes on port {self.port}...")
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.laddr.port == self.port and conn.status == 'LISTEN' and conn.pid:
                    proc = psutil.Process(conn.pid)
                    self.logger.warning(f"🔴 Port {self.port} is in use by PID {proc.pid} ({proc.name()}). Attempting to terminate...")
                    proc.kill() # Send SIGKILL
                    proc.wait(timeout=5) # Wait for termination
                    self.logger.info(f"✅ PID {proc.pid} terminated.")
                    return # Assume only one process needs to be killed for the port
        except psutil.NoSuchProcess:
            self.logger.debug(f"Process on port {self.port} already terminated during check.")
        except psutil.AccessDenied as e:
            self.logger.error(f"⚠️ Access denied trying to kill process on port {self.port}. Error: {e}")
        except Exception as e:
            self.logger.error(f"⚠️ An unexpected error occurred while trying to kill process on port {self.port}: {e}", exc_info=True)
        
        self.logger.debug(f"No active conflicting process found on port {self.port}, or termination handled.")


    def start_server(self, server_log_path: Path) -> Optional[subprocess.Popen]:
        self.logger.info(f"🔧 Launching ComfyUI server from: {self.comfyui_path}")
        self.logger.debug(f"Python executable: {self.python_executable}")
        self.logger.info(f"ComfyUI server output will be logged to: {server_log_path.name}")

        if not self.comfyui_path.exists() or not self.comfyui_path.is_dir():
            self.logger.error(f"ComfyUI path ({self.comfyui_path}) does not exist or is not a directory.")
            return None
        if not self.python_executable.exists() or not self.python_executable.is_file():
            self.logger.error(f"Python executable ({self.python_executable}) does not exist or is not a file.")
            return None

        main_py_path = self.comfyui_path / "main.py"
        if not main_py_path.exists():
            self.logger.error(f"ComfyUI main.py not found at {main_py_path}")
            return None

        command = [
            str(self.python_executable),
            str(main_py_path), # Use the full path to main.py
            f"--listen={self.host}",
            f"--port={self.port}",
            # Add any other essential ComfyUI arguments here
            # e.g., "--preview-method=auto"
        ]
        self.logger.info(f"Starting ComfyUI server with command: {' '.join(command)}")

        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        try:
            # Open the log file in append mode if you want to keep logs across restarts within a session
            # or 'w' to overwrite for each start_server call. 'w' is simpler for now.
            with open(server_log_path, "w", encoding="utf-8") as comfy_log_file:
                process = subprocess.Popen(
                    command, # Use the full command list
                    cwd=self.comfyui_path, # Set CWD to ComfyUI's root
                    stdout=comfy_log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=creation_flags
                )
            self.logger.info(f"ComfyUI server process started with PID: {process.pid}")
            self.server_process = process # Store the process
            return self.server_process
        except FileNotFoundError: # Should be less likely with explicit path checks above
            self.logger.error(f"Could not find 'main.py' or Python executable. Please check paths.", exc_info=True)
            self.server_process = None
            return None # Explicitly return None on failure
        except Exception as e:
            self.logger.exception(f"An unhandled error occurred while trying to launch the ComfyUI server: {e}")
            self.server_process = None
            return None # Explicitly return None on failure

    def wait_for_server_availability(self, retries=120, delay=1.0) -> bool:
        self.logger.info(f"Waiting for ComfyUI server to be available at http://{self.host}:{self.port}/")
        for i in range(retries):
            try:
                with socket.create_connection((self.host, self.port), timeout=1):
                    self.logger.info(f"✅ Server is available! (Attempt {i+1})")
                    return True
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                if i % 10 == 0 : # Log less frequently during wait
                    self.logger.debug(f"Server not yet available (attempt {i+1}/{retries}): {e}")
                time.sleep(delay)
        
        self.logger.error(f"Server at {self.host}:{self.port} did not become available after {retries * delay:.0f} seconds.")
        return False

    def shutdown_server(self): # No longer takes 'process' as an argument
        if not self.server_process or self.server_process.poll() is not None:
            self.logger.info("Server process not running or already exited.")
            self.server_process = None # Ensure it's cleared
            return

        process_to_terminate = self.server_process
        pid_to_terminate = process_to_terminate.pid
        self.logger.info(f"💤 Attempting to shut down ComfyUI server (PID: {pid_to_terminate})...")

        try:
            if platform.system() == "Windows":
                self.logger.debug(f"Sending CTRL_BREAK_EVENT to process group {pid_to_terminate} (Windows).")
                # This sends to the entire process group if CREATE_NEW_PROCESS_GROUP was used
                os.kill(pid_to_terminate, signal.CTRL_BREAK_EVENT)
            else:
                # On Linux/macOS, try to terminate the process group first
                try:
                    pgid = os.getpgid(pid_to_terminate)
                    self.logger.debug(f"Sending SIGTERM to process group {pgid} (Unix-like).")
                    os.killpg(pgid, signal.SIGTERM)
                except ProcessLookupError: # Process might have died quickly
                     self.logger.info(f"Process {pid_to_terminate} not found for SIGTERM, likely already exited.")
                except AttributeError: # os.getpgid might not be available on all POSIX-like systems
                    self.logger.debug(f"os.getpgid not available. Sending SIGTERM directly to process {pid_to_terminate}.")
                    process_to_terminate.send_signal(signal.SIGTERM) # Fallback to sending to just the process
                except Exception as e_pg: # Catch other potential errors with pgid/killpg
                    self.logger.warning(f"Error sending SIGTERM to process group {pid_to_terminate}: {e_pg}. Falling back to direct SIGTERM.")
                    process_to_terminate.send_signal(signal.SIGTERM)


            process_to_terminate.wait(timeout=10) # Wait for graceful exit
            self.logger.info(f"Server process {pid_to_terminate} exited gracefully.")
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Server process {pid_to_terminate} did not respond to graceful shutdown signal after 10s. Forcing termination (kill)...")
            process_to_terminate.kill() # Force kill
            try:
                process_to_terminate.wait(timeout=5) # Give kill some time
                self.logger.info(f"Server process {pid_to_terminate} force-killed.")
            except subprocess.TimeoutExpired:
                self.logger.error(f"Server process {pid_to_terminate} did not terminate even after force kill and 5s wait.")
            except Exception as e_kill_wait:
                 self.logger.error(f"Error waiting for process {pid_to_terminate} after kill: {e_kill_wait}", exc_info=True)
        except Exception as e: # Catch other potential errors like process already dead
            self.logger.error(f"An error occurred during server shutdown for PID {pid_to_terminate}: {e}", exc_info=True)
            if process_to_terminate.poll() is None: # If still running despite error
                self.logger.warning(f"Attempting to kill process {pid_to_terminate} due to prior shutdown error.")
                process_to_terminate.kill()
                try:
                    process_to_terminate.wait(timeout=5)
                    self.logger.info(f"Fallback kill successful for PID {pid_to_terminate}.")
                except Exception as kill_e:
                    self.logger.error(f"Fallback kill failed for PID {pid_to_terminate}: {kill_e}", exc_info=True)
        finally:
            self.server_process = None # Clear the stored process
