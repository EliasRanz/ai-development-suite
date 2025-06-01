import unittest
from unittest.mock import patch, MagicMock, mock_open, ANY
from pathlib import Path
import logging
import time
import subprocess # For spec and constants
import platform # For platform-specific logic
import signal # For signal constants like SIGTERM
import os # For os.kill, os.killpg, os.getpgid
import psutil # For psutil.Process spec

# Add project root to sys.path for imports from 'launcher'
import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.server_manager import ServerManager
# from comfy_launcher.config import Settings # Not directly used in this test file anymore

# Suppress logging output during tests unless specifically needed
# logging.disable(logging.CRITICAL)

class TestServerManager(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.mock_logger = MagicMock(spec=logging.Logger)

        self.mock_comfyui_path = MagicMock(spec=Path)
        self.mock_comfyui_path.name = "comfyui"
        self.mock_comfyui_path.__str__ = MagicMock(return_value="/fake/comfyui")
        
        self.mock_python_executable = MagicMock(spec=Path)
        self.mock_python_executable.name = "python"
        self.mock_python_executable.__str__ = MagicMock(return_value="/fake/venv/python")

        # Mock for comfyui_path / "main.py"
        self.mock_main_py = MagicMock(spec=Path)
        self.mock_main_py.exists.return_value = True # Default to main.py existing
        self.mock_main_py.__str__ = MagicMock(return_value="/fake/comfyui/main.py") # For logging/command
        self.mock_comfyui_path.__truediv__ = MagicMock(return_value=self.mock_main_py)


        # Default behavior for path checks (can be overridden in specific tests)
        self.mock_comfyui_path.exists.return_value = True
        self.mock_comfyui_path.is_dir.return_value = True
        self.mock_python_executable.exists.return_value = True
        self.mock_python_executable.is_file.return_value = True


        self.server_manager = ServerManager(
            comfyui_path=self.mock_comfyui_path,
            python_executable=self.mock_python_executable,
            host="127.0.0.1",
            port=8188,
            logger=self.mock_logger
        )
        self.test_host = "127.0.0.1"
        self.test_port = 8188


    @patch('comfy_launcher.server_manager.subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_start_server_success(self, mock_file_open, mock_popen_constructor):
        """Test successful server start."""
        # Ensure all path validations in start_server pass
        self.mock_comfyui_path.exists.return_value = True
        self.mock_comfyui_path.is_dir.return_value = True
        self.mock_python_executable.exists.return_value = True
        self.mock_python_executable.is_file.return_value = True
        self.mock_main_py.exists.return_value = True # Crucial for Popen to be called

        mock_process_instance = MagicMock() # Removed spec
        mock_process_instance.pid = 12345
        mock_popen_constructor.return_value = mock_process_instance

        server_log_path = Path("/fake/logs/server.log")

        process = self.server_manager.start_server(server_log_path)

        expected_command = [
            str(self.mock_python_executable),
            str(self.mock_main_py), 
            f"--listen={self.test_host}",
            f"--port={self.test_port}",
        ]
        expected_creationflags = 0
        if platform.system() == "Windows":
            expected_creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        mock_popen_constructor.assert_called_once_with(
            expected_command,
            cwd=self.mock_comfyui_path,
            stdout=mock_file_open.return_value,
            stderr=subprocess.STDOUT,
            creationflags=expected_creationflags
        )
        mock_file_open.assert_called_with(server_log_path, "w", encoding="utf-8")
        self.assertEqual(process, mock_process_instance)
        self.assertEqual(self.server_manager.server_process, mock_process_instance)
        self.mock_logger.info.assert_any_call(f"ComfyUI server process started with PID: 12345")

    def test_start_server_failure_comfyui_path_invalid(self):
        """Test server start failure if ComfyUI path is invalid."""
        self.mock_comfyui_path.exists.return_value = False
        server_log_path = Path("/fake/logs/server.log")
        process = self.server_manager.start_server(server_log_path)
        self.assertIsNone(process)
        self.mock_logger.error.assert_any_call(
            f"ComfyUI path ({self.mock_comfyui_path}) does not exist or is not a directory."
        )

    def test_start_server_failure_python_exe_invalid(self):
        """Test server start failure if Python executable path is invalid."""
        self.mock_python_executable.exists.return_value = False
        server_log_path = Path("/fake/logs/server.log")
        process = self.server_manager.start_server(server_log_path)
        self.assertIsNone(process)
        self.mock_logger.error.assert_any_call(
            f"Python executable ({self.mock_python_executable}) does not exist or is not a file."
        )

    def test_start_server_failure_main_py_not_found(self):
        """Test server start failure if main.py is not found in ComfyUI path."""
        self.mock_main_py.exists.return_value = False
        server_log_path = Path("/fake/logs/server.log")
        process = self.server_manager.start_server(server_log_path)
        self.assertIsNone(process)
        self.mock_logger.error.assert_any_call(
            f"ComfyUI main.py not found at {self.mock_main_py}"
        )

    @patch('comfy_launcher.server_manager.subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_start_server_failure_popen_filenotfound(self, mock_file_open, mock_popen_constructor):
        """Test server start failure due to Popen raising FileNotFoundError, which is caught by SUT."""
        # Ensure initial path checks pass so we reach the Popen call
        self.mock_comfyui_path.exists.return_value = True
        self.mock_comfyui_path.is_dir.return_value = True
        self.mock_python_executable.exists.return_value = True
        self.mock_python_executable.is_file.return_value = True
        self.mock_main_py.exists.return_value = True

        mock_popen_constructor.side_effect = FileNotFoundError("Fake Python not found by Popen")
        server_log_path = Path("/fake/logs/server.log")

        process = self.server_manager.start_server(server_log_path)

        self.assertIsNone(process) # start_server should return None
        # Check for the specific log message from the SUT's except FileNotFoundError block
        self.mock_logger.error.assert_any_call(
            "Could not find 'main.py' or Python executable. Please check paths.",
            exc_info=True
        )

    @patch('comfy_launcher.server_manager.socket.create_connection')
    @patch('comfy_launcher.server_manager.time.sleep', return_value=None)
    def test_wait_for_server_availability_success(self, mock_sleep, mock_create_connection):
        mock_create_connection.side_effect = [
            OSError("Connection refused"), OSError("Connection refused"), MagicMock()
        ]
        result = self.server_manager.wait_for_server_availability(retries=5, delay=0.01)
        self.assertTrue(result)
        self.assertEqual(mock_create_connection.call_count, 3)
        self.mock_logger.info.assert_any_call("✅ Server is available! (Attempt 3)")

    @patch('comfy_launcher.server_manager.socket.create_connection')
    @patch('comfy_launcher.server_manager.time.sleep', return_value=None)
    def test_wait_for_server_availability_failure_timeout(self, mock_sleep, mock_create_connection):
        mock_create_connection.side_effect = OSError("Connection refused")
        test_retries = 3
        test_delay = 0.01
        result = self.server_manager.wait_for_server_availability(retries=test_retries, delay=test_delay)
        self.assertFalse(result)
        self.assertEqual(mock_create_connection.call_count, test_retries)
        expected_seconds_str = f"{test_retries * test_delay:.0f}" # Format to 0 decimal places
        self.mock_logger.error.assert_any_call(
            f"Server at {self.test_host}:{self.test_port} did not become available after {expected_seconds_str} seconds."
        )

    @patch('comfy_launcher.server_manager.os.kill')
    @patch('comfy_launcher.server_manager.platform.system', return_value="Windows")
    @patch('comfy_launcher.server_manager.signal') # Patch the signal module used by SUT
    def test_shutdown_server_graceful_windows(self, mock_signal_sut, mock_platform_system, mock_os_kill):
        # Configure the SUT's view of signal.CTRL_BREAK_EVENT
        # Use getattr from the test's signal module if available, otherwise a known integer.
        mock_signal_sut.CTRL_BREAK_EVENT = getattr(signal, 'CTRL_BREAK_EVENT', 2)

        mock_process = MagicMock(spec=subprocess.Popen)
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = lambda timeout: setattr(mock_process, 'poll', MagicMock(return_value=0))
        self.server_manager.server_process = mock_process
        
        self.server_manager.shutdown_server() # No argument passed

        mock_os_kill.assert_called_once_with(mock_process.pid, mock_signal_sut.CTRL_BREAK_EVENT)
        mock_process.wait.assert_called_once_with(timeout=10)
        self.mock_logger.info.assert_any_call(f"Server process {mock_process.pid} exited gracefully.")
        mock_process.kill.assert_not_called()
        self.assertIsNone(self.server_manager.server_process)

    @patch('comfy_launcher.server_manager.os.killpg')
    @patch('comfy_launcher.server_manager.os.getpgid', return_value=54321)
    @patch('comfy_launcher.server_manager.platform.system', return_value="Linux")
    # No need to patch comfy_launcher.server_manager.signal here as SIGTERM is standard
    def test_shutdown_server_graceful_linux(self, mock_platform_system, mock_os_getpgid, mock_os_killpg):
        mock_process = MagicMock(spec=subprocess.Popen)
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = lambda timeout: setattr(mock_process, 'poll', MagicMock(return_value=0))
        self.server_manager.server_process = mock_process
        
        self.server_manager.shutdown_server() # No argument passed

        mock_os_getpgid.assert_called_once_with(mock_process.pid)
        mock_os_killpg.assert_called_once_with(54321, signal.SIGTERM) # SUT uses signal.SIGTERM directly
        mock_process.wait.assert_called_once_with(timeout=10)
        self.mock_logger.info.assert_any_call(f"Server process {mock_process.pid} exited gracefully.")
        mock_process.kill.assert_not_called()
        self.assertIsNone(self.server_manager.server_process)

    @patch('comfy_launcher.server_manager.os.kill')
    @patch('comfy_launcher.server_manager.os.killpg')
    @patch('comfy_launcher.server_manager.os.getpgid')
    @patch('comfy_launcher.server_manager.platform.system')
    @patch('comfy_launcher.server_manager.signal') # Patch signal for SUT
    def test_shutdown_server_force_kill(self, mock_signal_sut, mock_platform_system, mock_os_getpgid, mock_os_killpg, mock_os_kill_direct):
        # Configure SUT's signal.CTRL_BREAK_EVENT if platform is mocked to Windows
        if mock_platform_system.return_value == "Windows":
            mock_signal_sut.CTRL_BREAK_EVENT = getattr(signal, 'CTRL_BREAK_EVENT', 2)
        else: # For Linux, ensure SIGTERM is available (though it usually is)
            mock_signal_sut.SIGTERM = signal.SIGTERM


        mock_process = MagicMock(spec=subprocess.Popen)
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = [
            subprocess.TimeoutExpired(cmd="fake_cmd", timeout=10), None
        ]
        self.server_manager.server_process = mock_process
        
        self.server_manager.shutdown_server() # No argument passed

        if mock_platform_system.return_value == "Windows":
            mock_os_kill_direct.assert_any_call(mock_process.pid, mock_signal_sut.CTRL_BREAK_EVENT)
        else: # Assuming Linux or other POSIX
            mock_os_getpgid.assert_called_with(mock_process.pid)
            mock_os_killpg.assert_called_with(mock_os_getpgid.return_value, mock_signal_sut.SIGTERM)
        
        mock_process.wait.assert_any_call(timeout=10)
        self.mock_logger.warning.assert_any_call(f"Server process {mock_process.pid} did not respond to graceful shutdown signal after 10s. Forcing termination (kill)...")
        mock_process.kill.assert_called_once()
        mock_process.wait.assert_called_with(timeout=5)
        self.assertGreaterEqual(mock_process.wait.call_count, 2)
        self.mock_logger.info.assert_any_call(f"Server process {mock_process.pid} force-killed.")
        self.assertIsNone(self.server_manager.server_process)

    @patch('comfy_launcher.server_manager.psutil.Process')
    @patch('comfy_launcher.server_manager.psutil.net_connections')
    def test_kill_process_on_port_found_and_killed(self, mock_net_connections, mock_psutil_process_class):
        mock_conn = MagicMock()
        mock_conn.laddr.port = self.test_port
        mock_conn.status = 'LISTEN'
        mock_conn.pid = 6789
        mock_net_connections.return_value = [mock_conn]
        
        mock_proc_instance = MagicMock() # Removed spec
        mock_proc_instance.name.return_value = "python.exe"
        mock_proc_instance.pid = 6789
        mock_psutil_process_class.return_value = mock_proc_instance # This is the mock for psutil.Process()

        self.server_manager.kill_process_on_port()

        mock_psutil_process_class.assert_called_once_with(6789)
        mock_proc_instance.kill.assert_called_once()
        mock_proc_instance.wait.assert_called_once_with(timeout=5)
        self.mock_logger.info.assert_any_call(f"✅ PID {mock_proc_instance.pid} terminated.")

    @patch('comfy_launcher.server_manager.psutil.net_connections')
    def test_kill_process_on_port_not_found(self, mock_net_connections):
        """Test when no process is found on the port."""
        mock_net_connections.return_value = []
        self.server_manager.kill_process_on_port()
        # Corrected log message assertion
        self.mock_logger.debug.assert_any_call(
            f"No active conflicting process found on port {self.test_port}, or termination handled."
        )
        # Ensure the old, incorrect message is NOT called
        found_old_message = False
        for call_item in self.mock_logger.debug.call_args_list:
            if call_item[0][0] == f"No active process found on port {self.test_port}.":
                found_old_message = True
                break
        self.assertFalse(found_old_message, "Old log message should not be present.")

if __name__ == '__main__':
    unittest.main()
