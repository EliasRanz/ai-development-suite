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

from comfy_launcher.log_manager import LogManager

class TestLogManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)
        self.log_dir = self.temp_dir / "logs" # Consistent with LogManager's structure
        self.archive_dir = self.log_dir / "archive"
        
        self.patcher = patch('comfy_launcher.log_manager.logging.getLogger')
        self.mock_get_logger = self.patcher.start()
        
        self.mock_logger_instance = MagicMock(spec=logging.Logger)
        self.mock_logger_instance.handlers = [] 
        self.mock_logger_instance.hasHandlers.return_value = False
        # Make sure info, debug, error, warning methods exist on the mock logger
        for level_method in ['info', 'debug', 'error', 'warning', 'critical']:
            if not hasattr(self.mock_logger_instance, level_method):
                setattr(self.mock_logger_instance, level_method, MagicMock())

        self.mock_get_logger.return_value = self.mock_logger_instance

        # No longer patching builtins.print by default
        # self.print_patcher = patch('builtins.print')
        # self.mock_print = self.print_patcher.start()

    def tearDown(self):
        self.temp_dir_obj.cleanup()
        self.patcher.stop()
        # self.print_patcher.stop() # No longer patching print

    @patch('comfy_launcher.log_manager.LogManager._perform_log_rotation_and_cleanup')
    def test_log_manager_initialization_debug_mode(self, mock_perform_rotation):
        self.mock_logger_instance.reset_mock() 
        self.mock_logger_instance.handlers = []
        self.mock_logger_instance.hasHandlers.return_value = False 

        log_manager = LogManager(
            log_dir=self.log_dir, debug_mode=True,
            max_files_to_keep_in_archive=3, max_log_age_days=5
        )
        logger = log_manager.get_launcher_logger()
        
        mock_perform_rotation.assert_called_once()
        self.mock_get_logger.assert_called_with("ComfyUILauncher")
        self.mock_logger_instance.setLevel.assert_called_with(logging.DEBUG)
        self.assertGreaterEqual(self.mock_logger_instance.addHandler.call_count, 2)
        self.assertTrue(self.log_dir.exists())
        self.assertTrue(self.archive_dir.exists())

        mock_handler1 = MagicMock(spec=logging.Handler)
        mock_handler2 = MagicMock(spec=logging.Handler)
        
        self.mock_logger_instance.reset_mock() 
        self.mock_logger_instance.handlers = [mock_handler1, mock_handler2]
        self.mock_logger_instance.hasHandlers.return_value = True

        # Re-initialize to test handler cleanup
        log_manager_again = LogManager(
            log_dir=self.log_dir, debug_mode=True,
            max_files_to_keep_in_archive=3, max_log_age_days=5
        )

        mock_handler1.close.assert_called_once()
        mock_handler2.close.assert_called_once()
        self.mock_logger_instance.removeHandler.assert_has_calls(
            [call(mock_handler1), call(mock_handler2)], any_order=True
        )
        self.assertGreaterEqual(self.mock_logger_instance.addHandler.call_count, 2)
        self.assertEqual(logger, self.mock_logger_instance)
        self.assertEqual(log_manager_again.get_launcher_logger(), self.mock_logger_instance)


    @patch('comfy_launcher.log_manager.LogManager._perform_log_rotation_and_cleanup')
    def test_log_manager_initialization_production_mode(self, mock_perform_rotation):
        self.mock_logger_instance.reset_mock()
        self.mock_logger_instance.handlers = []
        self.mock_logger_instance.hasHandlers.return_value = False

        log_manager = LogManager(
            log_dir=self.log_dir, debug_mode=False,
            max_files_to_keep_in_archive=3, max_log_age_days=5
        )
        logger = log_manager.get_launcher_logger()

        mock_perform_rotation.assert_called_once()
        self.mock_get_logger.assert_called_with("ComfyUILauncher")
        self.mock_logger_instance.setLevel.assert_called_with(logging.INFO)
        self.assertEqual(logger, self.mock_logger_instance)

    @patch('comfy_launcher.log_manager.datetime')
    @patch('comfy_launcher.log_manager.os.rename')
    @patch('comfy_launcher.log_manager.LogManager._perform_log_rotation_and_cleanup') # Mock this out for focused test
    def test_internal_rotate_log_file(self, mock_perform_rotation, mock_os_rename, mock_datetime_module):
        mock_file_mtime = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime_module.fromtimestamp.return_value = mock_file_mtime

        # Instantiate LogManager, its __init__ will create dirs
        log_manager = LogManager(
            log_dir=self.log_dir, debug_mode=False,
            max_files_to_keep_in_archive=3, max_log_age_days=5
        )

        log_file_to_rotate = self.log_dir / "test.log"
        log_file_to_rotate.write_text("some log data") 
        
        # Call the instance method
        log_manager._rotate_log_file("test.log", log_manager.get_launcher_logger())
        
        expected_rotated_name = f"test_{mock_file_mtime.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        expected_target_path = self.archive_dir / expected_rotated_name
        
        mock_os_rename.assert_called_once_with(log_file_to_rotate, expected_target_path)
        mock_perform_rotation.assert_called_once() # From __init__

    @patch('comfy_launcher.log_manager.os.rename')
    @patch('comfy_launcher.log_manager.datetime')
    # Patch Path.exists specifically where it's used in _rotate_log_file
    @patch('comfy_launcher.log_manager.Path.exists')
    def test_internal_rotate_log_file_with_counter(self, mock_path_exists, mock_datetime_module, mock_os_rename):
        # Setup LogManager instance (mocking out __init__'s _perform_log_rotation_and_cleanup)
        with patch.object(LogManager, '_perform_log_rotation_and_cleanup'):
            log_manager = LogManager(
                log_dir=self.log_dir, debug_mode=False,
                max_files_to_keep_in_archive=3, max_log_age_days=5
            )

        mock_logger = log_manager.get_launcher_logger() # Or a fresh mock
        
        log_file_to_rotate = self.log_dir / "test.log"
        log_file_to_rotate.write_text("some log data")

        # Simulate log file modification time
        mock_file_mtime = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime_module.fromtimestamp.return_value = mock_file_mtime
        
        base_archive_name_no_ext, ext = os.path.splitext(f"test_{mock_file_mtime.strftime('%Y-%m-%d_%H-%M-%S')}.log")
        
        archive_path_original = self.archive_dir / f"{base_archive_name_no_ext}{ext}"
        archive_path_counter1 = self.archive_dir / f"{base_archive_name_no_ext}_1{ext}"
        archive_path_counter2 = self.archive_dir / f"{base_archive_name_no_ext}_2{ext}"

        # Sequence of Path.exists() calls in _rotate_log_file for "test.log":
        # 1. On log_file_to_rotate (source file) - should exist
        # 2. On archive_path_original (e.g., test_YYYY-MM-DD_HH-MM-SS.log) - simulate exists
        # 3. On archive_path_counter1 (e.g., test_YYYY-MM-DD_HH-MM-SS_1.log) - simulate exists
        # 4. On archive_path_counter2 (e.g., test_YYYY-MM-DD_HH-MM-SS_2.log) - simulate NOT exists (this one is chosen)
        # The mock_path_exists is for all Path.exists calls.
        # The first call in _rotate_log_file is `if log_file.exists():`
        # Then in the loop: `while archive_path.exists():`
        # So, the side_effect should cover these calls in order.
        # For this specific test, we are interested in the archive path checks.
        mock_path_exists.side_effect = [True, True, True, False] # Source exists, archive_original exists, archive_counter1 exists, archive_counter2 does NOT exist

        log_manager._rotate_log_file("test.log", mock_logger)

        mock_os_rename.assert_called_once_with(log_file_to_rotate, archive_path_counter2)
        mock_logger.info.assert_any_call(f"Rotated previous log 'test.log' to archive as '{archive_path_counter2.name}'")

    @patch('comfy_launcher.log_manager.datetime') # This mock_datetime_module is for the SUT
    @patch('comfy_launcher.log_manager.os.unlink')
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
        
        # Instantiate LogManager
        # The max_count and max_age_days are now instance attributes
        log_manager = LogManager(
            log_dir=self.log_dir, debug_mode=False,
            max_files_to_keep_in_archive=2, # This is max_count
            max_log_age_days=3             # This is max_age_days
        )

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
            file_path = self.archive_dir / name # Use instance's archive_dir
            file_path.write_text("dummy log content")
            os.utime(file_path, (dt_obj.timestamp(), dt_obj.timestamp()))
            created_file_path_objects[name] = file_path 
        
        # Call the instance method
        # _cleanup_archived_logs is called by _perform_log_rotation_and_cleanup during __init__
        # To test it in isolation, we can call it directly if needed, or test the effect of __init__
        # For this test, let's assume we are testing the method directly after setup.
        log_manager._cleanup_archived_logs("prefix", log_manager.get_launcher_logger())
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

    @patch('comfy_launcher.log_manager.LogManager._rotate_log_file')
    @patch('comfy_launcher.log_manager.LogManager._cleanup_archived_logs')
    def test_perform_log_rotation_and_cleanup_orchestration(self, mock_cleanup_archived, mock_rotate_file):
        max_files = 3 
        max_age_days = 5

        # Instantiate LogManager, which calls _perform_log_rotation_and_cleanup in __init__
        log_manager = LogManager(
            log_dir=self.log_dir, debug_mode=False,
            max_files_to_keep_in_archive=max_files,
            max_log_age_days=max_age_days
        )
        
        self.assertTrue(self.log_dir.exists())
        self.assertTrue(self.archive_dir.exists())
        
        # _perform_log_rotation_and_cleanup calls _rotate_log_file and _cleanup_archived_logs
        # So we check if these mocks (now methods of LogManager) were called correctly.
        # The logger passed to them will be the instance's logger.
        logger_arg = log_manager.get_launcher_logger()
        mock_rotate_file.assert_has_calls([
            call("launcher.log", logger_arg),
            call("server.log", logger_arg)
        ], any_order=True) 
        
        mock_cleanup_archived.assert_has_calls([
            call("launcher", logger_arg),
            call("server", logger_arg)
        ], any_order=True)

if __name__ == '__main__':
    unittest.main()