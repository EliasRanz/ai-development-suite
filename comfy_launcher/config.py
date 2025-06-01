from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import platform # Import the platform module
import re # For parsing resolv.conf
from typing import Literal # For type hinting the theme preference
# No need for set_key from dotenv if we are not saving from GUI

DOTENV_PATH = Path(__file__).resolve().parent / '.env'

class Settings(BaseSettings):
    """
    Centralized application configuration.
    Values can be overridden by creating a .env file in the 'launcher' directory.
    """
    DEBUG: bool = False
    COMFYUI_PATH: Path = Path(__file__).resolve().parent.parent.parent / "ComfyUI"
    HOST: str = "127.0.0.1" # This is what ComfyUI will --listen on
    PORT: int = 8188
    LOG_DIR_NAME: str = "logs"
    MAX_LOG_FILES: int = 3
    MAX_LOG_AGE_DAYS: int = 5
    APP_NAME: str = "ComfyUI Launcher"
    WINDOW_WIDTH: int = 1600
    WINDOW_HEIGHT: int = 900
    LAUNCHER_THEME: Literal["system", "light", "dark"] = "system"
    
    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )

    @property
    def LAUNCHER_ROOT(self) -> Path:
        return Path(__file__).resolve().parent
    @property
    def LOG_DIR(self) -> Path:
        return self.LAUNCHER_ROOT / self.LOG_DIR_NAME
    @property
    def PYTHON_EXECUTABLE(self) -> Path: # type: ignore[override]
        # Attempt to detect the Python executable within the ComfyUI .venv
        # This is more robust for cross-environment scenarios (e.g., WSL accessing Windows venv)
        
        venv_path = self.COMFYUI_PATH / ".venv"
        
        # Potential paths for the Python executable
        win_style_exec = venv_path / "Scripts" / "python.exe"
        unix_style_exec = venv_path / "bin" / "python"
        unix_style_exec3 = venv_path / "bin" / "python3" # Some Unix venvs might use python3

        if win_style_exec.exists() and win_style_exec.is_file():
            return win_style_exec
        elif unix_style_exec.exists() and unix_style_exec.is_file():
            return unix_style_exec
        elif unix_style_exec3.exists() and unix_style_exec3.is_file():
            return unix_style_exec3
        else:
            # Fallback to the original platform-based guess if no specific venv structure is found.
            # ServerManager will log an error if this path is also invalid.
            return win_style_exec if platform.system() == "Windows" else unix_style_exec
    @property
    def EFFECTIVE_CONNECT_HOST(self) -> str:
        """
        Determines the IP address the launcher should use to connect to ComfyUI
        (In this reverted state, it simply returns the configured HOST value).
        """
        # This reverts to the simplest behavior: always use the HOST setting.
        # If HOST is "127.0.0.1" and the launcher is in WSL,
        # it will attempt to connect to WSL's own loopback.
        return self.HOST
    @property
    def ASSETS_DIR(self) -> Path:
        return self.LAUNCHER_ROOT / "assets"

settings = Settings()

def get_all_current_settings() -> dict: # Still useful for debugging if needed
    """Returns all current settings values as a dictionary."""
    return Settings().model_dump()