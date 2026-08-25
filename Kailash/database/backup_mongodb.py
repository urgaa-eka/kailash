"""
MongoDB Backup Automation
Daily backups with 3-day retention
Company: Go4Garage | Domain: kailash-ai.in
"""
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backup")

BACKUP_DIR = Path("/app/backups")
RETENTION_DAYS = 3
DB_NAME = "kailash"


def create_backup():
    """Create MongoDB backup"""
    try:
        BACKUP_DIR.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"kailash_backup_{timestamp}"

        # MongoDB dump command
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")

        cmd = [
            "mongodump",
            "--uri", mongo_url,
            "--db", DB_NAME,
            "--out", str(backup_path)
        ]

        logger.info(f"Creating backup: {backup_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"[OK] Backup created successfully: {backup_path}")
            return True
        else:
            logger.error(f"[FAIL] Backup failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return False


def cleanup_old_backups():
    """Remove backups older than retention period"""
    try:
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)

        for backup in BACKUP_DIR.glob("kailash_backup_*"):
            if backup.is_dir():
                backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                if backup_time < cutoff_date:
                    logger.info(f"Removing old backup: {backup}")
                    subprocess.run(["rm", "-rf", str(backup)])

        logger.info("[OK] Cleanup completed")

    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting daily backup process...")

    if create_backup():
        cleanup_old_backups()
        logger.info("Backup process completed successfully")
    else:
        logger.error("[FAIL] Backup process failed")
        exit(1)
