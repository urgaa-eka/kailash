from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings
import logging
import asyncio

logger = logging.getLogger("kailash")

class MongoD:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB with optimized settings and retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Log database configuration for debugging
                if attempt == 0:
                    logger.info(f"MongoDB URL: {settings.MONGO_URL[:50]}...")
                    logger.info(f"Using database: {settings.DATABASE_NAME}")
                
                # Optimized connection parameters
                cls.client = AsyncIOMotorClient(
                    settings.MONGO_URL,
                    serverSelectionTimeoutMS=8000,  # Increased for Atlas
                    connectTimeoutMS=8000,           
                    socketTimeoutMS=15000,           # Longer socket timeout
                    maxPoolSize=20,                  # Increased pool size
                    minPoolSize=5,                   # Minimum connections
                    maxIdleTimeMS=30000,             # Connection idle time
                    retryWrites=True,
                    retryReads=True,
                    w="majority",                    # Write concern
                    readPreference="primaryPreferred"
                )
                
                # Verify connection with timeout
                await cls.client.admin.command('ping', maxTimeMS=8000)
                print(f"[OK] Connected to MongoDB at {settings.MONGO_URL[:50]}...")
                logger.info(f"✅ MongoDB connected to database: {settings.DATABASE_NAME}")
                return
                
            except Exception as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"[FAIL] Failed to connect to MongoDB after {max_retries} attempts: {e}")
                    logger.error(f"MongoDB connection failed permanently: {e}")
                    raise e
                else:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
    
    @classmethod
    async def close_db(cls):
        """Close MongoD connection"""
        if cls.client:
            cls.client.close()
            print("[OK] MongoD connection closed")
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        if not cls.client:
            raise Exception("MongoD client not initialized")
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection instance"""
        db = cls.get_database()
        return db[collection_name]

# Convenience function to get database
def get_db():
    return MongoD.get_database()
