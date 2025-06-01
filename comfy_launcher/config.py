from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import platform # Import the platform module
from typing import Literal
# No need for set_key from dotenv if we are not saving from GUI

DOTENV_PATH = Path(__file__).resolve().parent / '.env'

class Settings(BaseSettings):
    """
    Centralized application configuration.
    Values can be overridden by creating a .env file in the 'launcher' directory.
    """
    DEBUG: bool = False
    COMFYUI_PATH: Path = Path(__file__).resolve().parent.parent.parent / "ComfyUI"
    HOST: str = "127.0.0.1"
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
    def PYTHON_EXECUTABLE(self) -> Path:
        if platform.system() == "Windows":
            return self.COMFYUI_PATH / ".venv" / "Scripts" / "python.exe"
        else: # Linux, macOS, etc.
            return self.COMFYUI_PATH / ".venv" / "bin" / "python"
    @property
    def ASSETS_DIR(self) -> Path:
        return self.LAUNCHER_ROOT / "assets"

settings = Settings()

def get_all_current_settings() -> dict: # Still useful for debugging if needed
    """Returns all current settings values as a dictionary."""
    return Settings().model_dump()