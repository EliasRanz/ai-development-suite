import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import os
import tempfile

import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.config import Settings, get_all_current_settings # DOTENV_PATH is not needed in test file

class TestConfig(unittest.TestCase):

    def test_default_settings_load(self):
        """Test that default settings are loaded correctly when no .env or env vars are present."""
        # To test defaults, we instantiate Settings with a non-existent _env_file
        # and ensure actual environment variables are cleared for the test's scope.
        with patch.dict(os.environ, {}, clear=True):
            # Pass a non-existent path to _env_file to ensure it doesn't load any .env
            settings = Settings(_env_file=Path("/path/to/absolutely/non_existent_dummy.env"))
            self.assertEqual(settings.DEBUG, False)
            self.assertEqual(settings.HOST, "127.0.0.1")
            self.assertEqual(settings.PORT, 8188)
            self.assertEqual(settings.MAX_LOG_FILES, 3)
            self.assertIsInstance(settings.COMFYUI_PATH, Path)
            self.assertEqual(settings.LOG_DIR_NAME, "logs")
            self.assertEqual(settings.LAUNCHER_THEME, "system") # Test default theme

    def test_env_file_override(self):
        """Test that settings can be overridden by a .env file."""
        env_content = """
DEBUG=true
PORT=9999
COMFYUI_PATH="/custom/path/to/comfy"
MAX_LOG_FILES=7
LAUNCHER_THEME="dark"
        """
        # Create a real temporary .env file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".env") as tmp_env:
            tmp_env.write(env_content)
            tmp_env_path = Path(tmp_env.name)

        try:
            # Clear actual OS environment variables to isolate test to .env file
            with patch.dict(os.environ, {}, clear=True):
                # Instantiate Settings directly, telling it to use our temporary .env file
                settings_from_env = Settings(_env_file=tmp_env_path)
                
                self.assertEqual(settings_from_env.DEBUG, True)
                self.assertEqual(settings_from_env.PORT, 9999)
                self.assertEqual(str(settings_from_env.COMFYUI_PATH), "/custom/path/to/comfy")
                self.assertEqual(settings_from_env.MAX_LOG_FILES, 7)
                self.assertEqual(settings_from_env.LAUNCHER_THEME, "dark") # Test theme override
        finally:
            os.unlink(tmp_env_path) # Clean up

    def test_derived_properties_log_dir(self):
        """Test a derived property like LOG_DIR."""
        with patch.dict(os.environ, {}, clear=True):
            # Instantiate with a non-existent env_file to test defaults for base paths
            s = Settings(_env_file=Path("/path/to/absolutely/non_existent_dummy.env"))
            
            # LAUNCHER_ROOT is derived from the location of config.py
            expected_launcher_root = Path(sys.modules['comfy_launcher.config'].__file__).resolve().parent
            expected_log_dir = expected_launcher_root / "logs" # Assuming LOG_DIR_NAME default is "logs"
            
            self.assertEqual(s.LAUNCHER_ROOT, expected_launcher_root)
            self.assertEqual(s.LOG_DIR, expected_log_dir)

    def test_get_all_current_settings(self):
        """Test the get_all_current_settings function."""
        # Test with defaults by ensuring get_all_current_settings internally uses a non-existent .env
        with patch.object(Settings, 'model_config', new={'env_file': Path("/path/to/non_existent_dummy.env"), 'extra': 'ignore'}), \
             patch.dict(os.environ, {}, clear=True):
            current_settings = get_all_current_settings()
            self.assertIsInstance(current_settings, dict)
            self.assertEqual(current_settings['DEBUG'], False)
            self.assertEqual(current_settings['PORT'], 8188)

        # Test with a temporary .env override
        env_content = "PORT=1234\nAPP_NAME=\"Test App via Env\"\n"
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".env") as tmp_env:
            tmp_env.write(env_content)
            tmp_env_path_str = tmp_env.name
        
        try:
            # To make get_all_current_settings use this temp .env, we patch Settings' model_config
            # This is a bit more involved as get_all_current_settings creates its own Settings instance.
            original_model_config = Settings.model_config

            # Temporarily change the model_config for the Settings class itself
            # so any new instance created by get_all_current_settings will use it.
            Settings.model_config = {'env_file': Path(tmp_env_path_str), 'extra': 'ignore', 'env_file_encoding': 'utf-8'}

            with patch.dict(os.environ, {}, clear=True):
                current_settings_env = get_all_current_settings()
                self.assertEqual(current_settings_env['PORT'], 1234)
                self.assertEqual(current_settings_env['APP_NAME'], "Test App via Env")
        finally:
            Settings.model_config = original_model_config # Restore original model_config
            os.unlink(tmp_env_path_str)

if __name__ == '__main__':
    unittest.main()