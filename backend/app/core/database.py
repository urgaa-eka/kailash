from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger("kailash")

class DatabaseManager:
    def __init__(self):
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db = None
    
    async def connect_all(self):
        """Connect to MongoDB"""
        if hasattr(settings, 'MONGO_URL') and settings.MONGO_URL:
            try:
                self.mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
                self.mongo_db = self.mongo_client[settings.DATABASE_NAME]
                logger.info("MongoDB connected")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {str(e)}")
                raise
    
    async def close_all(self):
        """Close database connections"""
        if self.mongo_client:
            self.mongo_client.close()
    
    async def get_mongo_db(self):
        """Get MongoDB database"""
        return self.mongo_db

db_manager = DatabaseManager()

async def get_mongo_db():
    return db_manager.mongo_db
