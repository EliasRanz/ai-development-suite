import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# --- Launcher's Own Logger ---

def setup_launcher_logger(log_dir: Path, debug_mode: bool) -> logging.Logger:
    """Configures and returns the logger for the launcher application itself."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ComfyUILauncher") 
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    if logger.hasHandlers():
        for handler in logger.handlers[:]: 
            handler.close()
            logger.removeHandler(handler)

    console_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    launcher_log_file = log_dir / "launcher.log"
    file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)-8s] %(message)s")
    file_handler = logging.FileHandler(launcher_log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info("=" * 50)
    logger.info("Launcher logger initialized for new session.")
    return logger


# --- Log File Rotation and Cleanup Utilities ---

def _rotate_log_file(log_dir: Path, archive_dir: Path, basename: str):
    log_file = log_dir / basename
    if log_file.exists():
        if log_file.stat().st_size > 0: 
            try:
                timestamp = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d_%H-%M-%S")
                base, ext = os.path.splitext(basename)
                rotated_name = f"{base}_{timestamp}{ext}"
                destination = archive_dir / rotated_name
                
                counter = 0
                while destination.exists():
                    counter += 1
                    rotated_name = f"{base}_{timestamp}_{counter}{ext}"
                    destination = archive_dir / rotated_name
                
                os.rename(log_file, destination) 
                print(f"[INFO] Rotated previous log '{log_file.name}' to archive as '{destination.name}'")
            except Exception as e:
                print(f"[ERROR] Could not rotate log file {log_file}: {e}")
        else: 
            try:
                os.unlink(log_file)
                print(f"[INFO] Deleted empty previous log file: {log_file.name}")
            except Exception as e:
                print(f"[ERROR] Could not delete empty log file {log_file}: {e}")


def _cleanup_backups(archive_dir: Path, base_name: str, max_count: int, max_age_days: int):
    logger = logging.getLogger("ComfyUILauncher") 
    logger.info(f"Cleaning up old '{base_name}' logs from archive: {archive_dir}")
    try:
        now = datetime.now()
        
        backup_logs = sorted(
            archive_dir.glob(f"{base_name}_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        logger.debug(f"Found {len(backup_logs)} archived '{base_name}' logs for potential cleanup.")

        files_to_delete = set()
        
        for i, log_file in enumerate(backup_logs):
            age = now - datetime.fromtimestamp(log_file.stat().st_mtime)
            marked_for_deletion_this_file = False
            reason_parts = []

            if age.days >= max_age_days:
                marked_for_deletion_this_file = True
                reason_parts.append(f"age {age.days}d >= {max_age_days}d")
            
            if i >= max_count: 
                marked_for_deletion_this_file = True
                reason_parts.append(f"index {i} >= files_to_keep_count {max_count}")
            
            if marked_for_deletion_this_file:
                files_to_delete.add(log_file)
                logger.debug(f"Marking for deletion: {log_file.name} (Reason: {'; '.join(reason_parts)})")
        
        if not files_to_delete:
            logger.info(f"No old '{base_name}' logs from '{archive_dir}' met criteria for deletion.")
            return

        logger.debug(f"Files actually marked for deletion: {[f.name for f in files_to_delete]}")
        for log_file_to_delete in files_to_delete:
            try:
                logger.debug(f"Attempting to os.unlink: {log_file_to_delete}")
                os.unlink(log_file_to_delete) 
                logger.info(f"🗑️ Deleted archived log: {log_file_to_delete.name}")
            except OSError as e:
                logger.warning(f"Could not delete archived log {log_file_to_delete.name}: {e}")
            
    except Exception as e:
        logger.error(f"An error occurred during log cleanup for '{base_name}' in {archive_dir}: {e}", exc_info=True)


def rotate_and_cleanup_logs(log_dir: Path, max_files_to_keep_in_archive: int, max_log_age_days: int):
    archive_dir = log_dir / "archive"
    log_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(exist_ok=True) 
    
    print(f"[INFO] Rotating previous session logs (if any) into: {archive_dir}")
    _rotate_log_file(log_dir, archive_dir, "launcher.log")
    _rotate_log_file(log_dir, archive_dir, "server.log")

    print(f"[INFO] Cleaning up old archived logs...")
    _cleanup_backups(archive_dir, "launcher", max_files_to_keep_in_archive, max_log_age_days)
    _cleanup_backups(archive_dir, "server", max_files_to_keep_in_archive, max_log_age_days)