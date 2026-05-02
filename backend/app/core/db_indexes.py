"""
Database Indexes Configuration
Defines indexes for optimal query performance in production
"""
from motor.motor_asyncio import AsyncIOMotorClient
from .mongodb import MongoD
import logging

logger = logging.getLogger("kailash")

async def create_indexes():
    """
    Create database indexes for optimal performance
    Called during application startup
    
    Note: In production Atlas environments, index creation may be restricted.
    The application will continue to function without indexes, though with reduced performance.
    """
    try:
        # Check if MongoD is connected before attempting to create indexes
        if MongoD.client is None:
            logger.warning("[WARN] MongoD not connected, skipping index creation")
            return
        
        db = MongoD.get_database()
        
        # Helper function to safely create index with permission error handling
        async def safe_create_index(collection, index_spec, **kwargs):
            try:
                await collection.create_index(index_spec, **kwargs)
                return True
            except Exception as idx_error:
                # Check if it's an authorization error (code 13)
                if hasattr(idx_error, 'code') and idx_error.code == 13:
                    logger.info(f"[INFO] Index creation skipped for {collection.name} (Atlas managed) - indexes may already exist")
                    return False
                # Re-raise other errors
                raise idx_error
        
        # Tasks collection indexes
        success_count = 0
        if await safe_create_index(db.tasks, "status"):
            success_count += 1
        if await safe_create_index(db.tasks, "assigned_department"):
            success_count += 1
        if await safe_create_index(db.tasks, "priority"):
            success_count += 1
        if await safe_create_index(db.tasks, [("created_at", -1)]):
            success_count += 1
        if success_count > 0:
            logger.info(f"[OK] Created {success_count} indexes on tasks collection")
        
        # GANESHA commands collection indexes
        success_count = 0
        if await safe_create_index(db.ganesha_commands, "user_id"):
            success_count += 1
        if await safe_create_index(db.ganesha_commands, "processing_status"):
            success_count += 1
        if await safe_create_index(db.ganesha_commands, [("created_at", -1)]):
            success_count += 1
        if success_count > 0:
            logger.info(f"[OK] Created {success_count} indexes on ganesha_commands collection")
        
        # Activities collection indexes
        success_count = 0
        if await safe_create_index(db.activities, "type"):
            success_count += 1
        if await safe_create_index(db.activities, [("created_at", -1)]):
            success_count += 1
        if success_count > 0:
            logger.info(f"[OK] Created {success_count} indexes on activities collection")
        
        # Departments collection indexes
        success_count = 0
        if await safe_create_index(db.departments, "id", unique=True):
            success_count += 1
        if await safe_create_index(db.departments, "status"):
            success_count += 1
        if success_count > 0:
            logger.info(f"[OK] Created {success_count} indexes on departments collection")
        
        # Users collection indexes
        success_count = 0
        if await safe_create_index(db.users, "email", unique=True):
            success_count += 1
        if await safe_create_index(db.users, "kailash_code", unique=True):
            success_count += 1
        if success_count > 0:
            logger.info(f"[OK] Created {success_count} indexes on users collection")
        
        logger.info("[OK] Database index creation completed (Atlas may manage indexes automatically)")
        
    except Exception as e:
        # Don't crash the application if index creation fails
        # In managed Atlas environments, indexes may be pre-configured or restricted
        logger.info(f"[INFO] Index creation completed with restrictions: {str(e)[:100]}")
        logger.info("[INFO] Application will continue - performance optimizations may be managed by Atlas")
