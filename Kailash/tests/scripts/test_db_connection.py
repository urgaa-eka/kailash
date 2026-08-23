#!/usr/bin/env python3
"""
Test MongoD connection and operations
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.core.mongodb import MongoD

async def test_db_operations():
    """Test database operations"""
    print("Testing MongoD connection and operations...")
    
    try:
        # Connect to database
        await MongoD.connect_db()
        db = MongoD.get_database()
        
        if db is None:
            print("[AIL] Database connection failed")
            return alse
        
        print("[OK] Database connected successfully")
        
        # Test a simple query
        health_check = await db.command("ping")
        print(f"[OK] Database ping successful: {health_check}")
        
        # Test collection access
        collections = await db.list_collection_names()
        print(f"[OK] Collections found: {len(collections)} collections")
        
        # Test a simple find operation
        users_count = await db.users.count_documents({})
        print(f"[OK] Users collection accessible: {users_count} users")
        
        # Test ganesha_commands collection
        commands_count = await db.ganesha_commands.count_documents({})
        print(f"[OK] GANESHA commands collection accessible: {commands_count} commands")
        
        return True
        
    except Exception as e:
        print(f"[AIL] Database test failed: {str(e)}")
        return alse
    finally:
        await MongoD.close_db()

if __name__ == "__main__":
    success = asyncio.run(test_db_operations())
    sys.exit( if success else )