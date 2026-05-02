"""
Pytest configuration for test suite
Configures test database and fixtures
"""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Test database configuration
TEST_MONGO_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "kailash_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Setup test database"""
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = client[TEST_DB_NAME]
    
    # Create test user
    await db.users.insert_one({
        "kailash_code": "<REDACTED_kailash_code>",
        "password": "$2b$12$REDACTED_BCRYPT_HASH_PLACEHOLDER____________________",  # <REDACTED_PASSWORD>
        "name": "Test User",
        "role": "admin",
        "two_factor_enabled": False
    })
    
    # Create test departments
    departments = [
        {"name": "GANESHA", "description": "AI Orchestrator"},
        {"name": "VISHWAKARMA", "description": "Engineering"},
        {"name": "SURYA", "description": "URGAA Product"},
        {"name": "TVASHTA", "description": "GSTSAAS Product"},
        {"name": "KARTIKEYA", "description": "IGNITION Product"},
        {"name": "LAKSHMI", "description": "CFO"},
        {"name": "KUBERA", "description": "Sales"},
        {"name": "KAMADEVA", "description": "Marketing"}
    ]
    await db.departments.insert_many(departments)
    
    yield db
    
    # Cleanup
    await client.drop_database(TEST_DB_NAME)
    client.close()

@pytest.fixture(scope="session")
def override_get_db(test_db):
    """Override database dependency for tests"""
    async def _override():
        return test_db
    return _override
