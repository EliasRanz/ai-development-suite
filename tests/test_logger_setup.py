import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import logging
import tempfile
from datetime import datetime, timedelta
import os 

import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.logger_setup import setup_launcher_logger, rotate_and_cleanup_logs, _rotate_log_file, _cleanup_backups

class TestLoggerSetup(unittest.TestCase):

    def setUp(self):
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)
        
        self.patcher = patch('comfy_launcher.logger_setup.logging.getLogger')
        self.mock_get_logger = self.patcher.start()
        
        self.mock_logger_instance = MagicMock(spec=logging.Logger)
        self.mock_logger_instance.handlers = [] 
        self.mock_logger_instance.hasHandlers.return_value = False
        self.mock_get_logger.return_value = self.mock_logger_instance

        # No longer patching builtins.print by default
        # self.print_patcher = patch('builtins.print')
        # self.mock_print = self.print_patcher.start()

    def tearDown(self):
        self.temp_dir_obj.cleanup()
        self.patcher.stop()
        # self.print_patcher.stop() # No longer patching print

    def test_setup_launcher_logger_debug_mode(self):
        self.mock_logger_instance.reset_mock() 
        self.mock_logger_instance.handlers = []
        self.mock_logger_instance.hasHandlers.return_value = False 

        logger = setup_launcher_logger(self.temp_dir, debug_mode=True)
        
        self.mock_get_logger.assert_called_with("ComfyUILauncher")
        self.mock_logger_instance.setLevel.assert_called_with(logging.DEBUG)
        self.assertGreaterEqual(self.mock_logger_instance.addHandler.call_count, 2)

        mock_handler1 = MagicMock(spec=logging.Handler)
        mock_handler2 = MagicMock(spec=logging.Handler)
        
        self.mock_logger_instance.reset_mock() 
        self.mock_logger_instance.handlers = [mock_handler1, mock_handler2]
        self.mock_logger_instance.hasHandlers.return_value = True
        
        logger_again = setup_launcher_logger(self.temp_dir, debug_mode=True)
        
        mock_handler1.close.assert_called_once()
        mock_handler2.close.assert_called_once()
        self.mock_logger_instance.removeHandler.assert_has_calls(
            [call(mock_handler1), call(mock_handler2)], any_order=True
        )
        self.assertGreaterEqual(self.mock_logger_instance.addHandler.call_count, 2)


    def test_setup_launcher_logger_production_mode(self):
        self.mock_logger_instance.reset_mock()
        self.mock_logger_instance.handlers = []
        self.mock_logger_instance.hasHandlers.return_value = False

        logger = setup_launcher_logger(self.temp_dir, debug_mode=False)
        self.mock_get_logger.assert_called_with("ComfyUILauncher")
        self.mock_logger_instance.setLevel.assert_called_with(logging.INFO)

    @patch('comfy_launcher.logger_setup.datetime')
    @patch('comfy_launcher.logger_setup.os.rename')
    def test_rotate_log_file(self, mock_os_rename, mock_datetime_module):
        mock_file_mtime = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime_module.fromtimestamp.return_value = mock_file_mtime

        archive_dir = self.temp_dir / "archive"
        archive_dir.mkdir()

        log_file_to_rotate = self.temp_dir / "test.log"
        log_file_to_rotate.write_text("some log data") 
        
        _rotate_log_file(self.temp_dir, archive_dir, "test.log")
        
        expected_rotated_name = f"test_{mock_file_mtime.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        expected_target_path = archive_dir / expected_rotated_name
        
        mock_os_rename.assert_called_once_with(log_file_to_rotate, expected_target_path)

    @patch('comfy_launcher.logger_setup.datetime') # This mock_datetime_module is for the SUT
    @patch('comfy_launcher.logger_setup.os.unlink')
    def test_cleanup_backups_by_age_and_count(self, mock_os_unlink, mock_datetime_module_sut): # Renamed mock for clarity
        # Use the real datetime for setting up 'now' in the test
        now_for_test = datetime(2023, 1, 10, 12, 0, 0)
        mock_datetime_module_sut.now.return_value = now_for_test 

        # Configure SUT's datetime.fromtimestamp to call the REAL datetime.fromtimestamp
        # This requires importing the real datetime module with an alias in the test file
        # (already done at the top of this file in previous versions)
        # If 'real_datetime_module' alias isn't set up, this line will fail.
        # Assuming 'import datetime as real_datetime_module' is at the top.
        # For clarity, let's ensure it's explicitly available if not imported with that alias:
        import datetime as actual_datetime_for_side_effect
        mock_datetime_module_sut.fromtimestamp.side_effect = actual_datetime_for_side_effect.datetime.fromtimestamp


        archive_dir = self.temp_dir / "archive" 
        archive_dir.mkdir(exist_ok=True)

        log_files_data = {
            "prefix_2023-01-09_10-00-00.log": (now_for_test - timedelta(days=1)),
            "prefix_2023-01-08_10-00-00.log": (now_for_test - timedelta(days=2)),
            "prefix_2023-01-07_10-00-00.log": (now_for_test - timedelta(days=3)),
            "prefix_2023-01-06_10-00-00.log": (now_for_test - timedelta(days=4)),
            "prefix_2023-01-05_10-00-00.log": (now_for_test - timedelta(days=5)),
            "prefix_2023-01-04_10-00-00.log": (now_for_test - timedelta(days=6))
        }
        
        created_file_path_objects = {}
        for name, dt_obj in log_files_data.items():
            file_path = archive_dir / name
            file_path.write_text("dummy log content")
            os.utime(file_path, (dt_obj.timestamp(), dt_obj.timestamp()))
            created_file_path_objects[name] = file_path 
        
        _cleanup_backups(archive_dir=archive_dir, base_name="prefix", max_count=2, max_age_days=3)

        expected_deleted_paths = {
            created_file_path_objects["prefix_2023-01-07_10-00-00.log"],
            created_file_path_objects["prefix_2023-01-06_10-00-00.log"],
            created_file_path_objects["prefix_2023-01-05_10-00-00.log"],
            created_file_path_objects["prefix_2023-01-04_10-00-00.log"]
        }
            
        called_unlink_on_paths = set()
        if mock_os_unlink.called:
            for call_args_tuple in mock_os_unlink.call_args_list:
                called_unlink_on_paths.add(call_args_tuple[0][0]) 
        
        self.assertSetEqual(called_unlink_on_paths, expected_deleted_paths)


    @patch('comfy_launcher.logger_setup._rotate_log_file')
    @patch('comfy_launcher.logger_setup._cleanup_backups')
    def test_rotate_and_cleanup_logs_orchestration(self, mock_cleanup, mock_rotate):
        log_dir = self.temp_dir / "logs" 
        archive_dir_expected = log_dir / "archive"
        max_files = 3 
        max_age_days = 5
        
        rotate_and_cleanup_logs(log_dir, max_files, max_age_days)
        
        self.assertTrue(log_dir.exists())
        self.assertTrue(archive_dir_expected.exists())
        
        mock_rotate.assert_has_calls([
            call(log_dir, archive_dir_expected, "launcher.log"),
            call(log_dir, archive_dir_expected, "server.log")
        ], any_order=True) 
        
        mock_cleanup.assert_has_calls([
            call(archive_dir_expected, "launcher", max_files, max_age_days),
            call(archive_dir_expected, "server", max_files, max_age_days)
        ], any_order=True)

if __name__ == '__main__':
    unittest.main()