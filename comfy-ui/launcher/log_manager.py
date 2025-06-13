import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

class LogManager:
    def __init__(self, log_dir: Path, debug_mode: bool, 
                 max_files_to_keep_in_archive: int, max_log_age_days: int):
        self.log_dir = log_dir
        self.archive_dir = self.log_dir / "archive"
        self.debug_mode = debug_mode
        self.max_files_to_keep_in_archive = max_files_to_keep_in_archive
        self.max_log_age_days = max_log_age_days

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)

        # Perform rotation and cleanup of previous session's logs first.
        # Note: This will use a temporary basic logger for its own messages if self.launcher_logger isn't set.
        # Or, we can pre-initialize a console-only logger for LogManager's internal operations.
        self._perform_log_rotation_and_cleanup()
        self.launcher_logger = self._setup_launcher_logger() # Now setup the logger for the current session

    def _setup_launcher_logger(self) -> logging.Logger:
        """Configures and returns the logger for the launcher application itself."""
        logger = logging.getLogger("ComfyUILauncher")
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)

        if logger.hasHandlers():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        # Console Handler (always added)
        console_formatter = logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        logger.addHandler(console_handler)

        launcher_log_file = self.log_dir / "launcher.log"
        # File Handler (always added, level determined by logger.setLevel)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s")
        file_handler = logging.FileHandler(launcher_log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info("=" * 50)
        logger.info("Launcher logger initialized for new session.")
        return logger

    def get_launcher_logger(self) -> logging.Logger:
        """Returns the configured launcher logger instance."""
        return self.launcher_logger

    def _rotate_log_file(self, basename: str, logger_to_use: logging.Logger):
        log_file = self.log_dir / basename
        if log_file.exists():
            if log_file.stat().st_size > 0:
                try:
                    timestamp = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d_%H-%M-%S")
                    base, ext = os.path.splitext(basename)
                    rotated_name = f"{base}_{timestamp}{ext}"
                    destination = self.archive_dir / rotated_name

                    counter = 0
                    while destination.exists():
                        counter += 1
                        rotated_name = f"{base}_{timestamp}_{counter}{ext}"
                        destination = self.archive_dir / rotated_name

                    os.rename(log_file, destination)
                    logger_to_use.info(f"Rotated previous log '{log_file.name}' to archive as '{destination.name}'")
                except Exception as e:
                    logger_to_use.error(f"Could not rotate log file {log_file}: {e}", exc_info=True)
            else:
                try:
                    os.unlink(log_file)
                    logger_to_use.info(f"Deleted empty previous log file: {log_file.name}")
                except Exception as e:
                    logger_to_use.error(f"Could not delete empty log file {log_file}: {e}", exc_info=True)

    def _cleanup_archived_logs(self, base_name: str, logger_to_use: logging.Logger):
        logger_to_use.info(f"Cleaning up old '{base_name}' logs from archive: {self.archive_dir}")
        try:
            now = datetime.now()
            backup_logs = sorted(
                self.archive_dir.glob(f"{base_name}_*.log"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            logger_to_use.debug(f"Found {len(backup_logs)} archived '{base_name}' logs for potential cleanup.")

            files_to_delete = set()
            for i, log_file in enumerate(backup_logs):
                age = now - datetime.fromtimestamp(log_file.stat().st_mtime)
                marked_for_deletion_this_file = False
                reason_parts = []

                if age.days >= self.max_log_age_days:
                    marked_for_deletion_this_file = True
                    reason_parts.append(f"age {age.days}d >= {self.max_log_age_days}d")

                if i >= self.max_files_to_keep_in_archive:
                    marked_for_deletion_this_file = True
                    reason_parts.append(f"index {i} >= files_to_keep_count {self.max_files_to_keep_in_archive}")

                if marked_for_deletion_this_file:
                    files_to_delete.add(log_file)
                    logger_to_use.debug(f"Marking for deletion: {log_file.name} (Reason: {'; '.join(reason_parts)})")

            if not files_to_delete:
                logger_to_use.info(f"No old '{base_name}' logs from '{self.archive_dir}' met criteria for deletion.")
                return

            for log_file_to_delete in files_to_delete:
                try:
                    os.unlink(log_file_to_delete)
                    logger_to_use.info(f"🗑️ Deleted archived log: {log_file_to_delete.name}")
                except OSError as e:
                    logger_to_use.warning(f"Could not delete archived log {log_file_to_delete.name}: {e}")
        except Exception as e:
            logger_to_use.error(f"An error occurred during log cleanup for '{base_name}' in {self.archive_dir}: {e}", exc_info=True)

    def _perform_log_rotation_and_cleanup(self):
        # Temporarily use a basic console logger if self.launcher_logger isn't fully set up yet,
        # or ensure self.launcher_logger is at least console-ready before this.
        # For simplicity, we'll assume self.launcher_logger might not have its file handler yet.
        # The initial log messages from this method might only go to console if called before full setup.
        # A more robust way would be to pass a logger or use logging.getLogger(__name__) here.
        _internal_logger = self.launcher_logger if hasattr(self, 'launcher_logger') and self.launcher_logger else logging.getLogger(__name__)
        _internal_logger.info(f"Rotating previous session logs (if any) into: {self.archive_dir}")
        self._rotate_log_file("launcher.log", _internal_logger)
        self._rotate_log_file("server.log", _internal_logger) # Manages server.log rotation

        _internal_logger.info(f"Cleaning up old archived logs...")
        self._cleanup_archived_logs("launcher", _internal_logger)
        self._cleanup_archived_logs("server", _internal_logger) # Manages server.log cleanup
