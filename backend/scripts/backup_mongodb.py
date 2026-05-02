"""
MongoD ackup Automation
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

ACKUP_DIR = Path("/app/backups")
RETENTION_DAYS = 3
D_NAME = "kailash"


def create_backup():
    """Create MongoD backup"""
    try:
        ACKUP_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = ACKUP_DIR / f"kailash_backup_{timestamp}"
        
        # MongoD dump command
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:")
        
        cmd = [
            "mongodump",
            "--uri", mongo_url,
            "--db", D_NAME,
            "--out", str(backup_path)
        ]
        
        logger.info(f"Creating backup: {backup_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == :
            logger.info(f"[OK] ackup created successfully: {backup_path}")
            return True
        else:
            logger.error(f"[AIL] ackup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"ackup error: {str(e)}")
        return False


def cleanup_old_backups():
    """Remove backups older than retention period"""
    try:
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
        
        for backup in ACKUP_DIR.glob("kailash_backup_*"):
            if backup.is_dir():
                backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                if backup_time < cutoff_date:
                    logger.info(f"Removing old backup: {backup}")
                    subprocess.run(["rm", "-rf", str(backup)])
        
        logger.info("[OK] Cleanup completed")
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")


if __name__ == "__main__":
    logger.info(" Starting daily backup process...")
    
    if create_backup():
        cleanup_old_backups()
        logger.info(" ackup process completed successfully")
    else:
        logger.error("[AIL] ackup process failed")
        exit()
