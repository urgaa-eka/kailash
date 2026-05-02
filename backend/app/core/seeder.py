"""
Kailash - Production Database Auto-Seeder
This script automatically seeds required data when the application starts
in a fresh production environment (Atlas MongoDB).
"""

import asyncio
import logging
import warnings
from datetime import datetime
# Suppress bcrypt version warning from passlib
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("kailash.seeder")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default admin user for production
DEFAULT_ADMIN = {
    "id": "2b03875f-bb4a-4330-8c22-0fe45a9969d0",
    "email": "admin@kailash.ai",
    "kailash_code": "KAILASH001",
    "full_name": "Kailash Admin",
    "role": "super_admin",
    "department": "Administration",
    "is_admin": True,
    "is_active": True,
    "two_factor_enabled": False,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# 20 AI Departments
DEPARTMENTS = [
    {"id": "dept-001", "name": "GANESHA", "description": "Master Orchestrator - Removes obstacles in operations", "deity": "Lord Ganesha", "color": "#FF6B6B", "icon": "brain", "workload": 7, "status": "active", "sub_agents": 4},
    {"id": "dept-002", "name": "VISHWAKARMA", "description": "Infrastructure & Architecture", "deity": "Lord Vishwakarma", "color": "#4ECDC4", "icon": "building", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-003", "name": "SURYA", "description": "Energy Management & Solar Integration", "deity": "Lord Surya", "color": "#FFE66D", "icon": "sun", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-004", "name": "TVASHTA", "description": "Manufacturing & Production", "deity": "Lord Tvashta", "color": "#95E1D3", "icon": "factory", "workload": 4, "status": "active", "sub_agents": 3},
    {"id": "dept-005", "name": "KARTIKEYA", "description": "Security & Defense Operations", "deity": "Lord Kartikeya", "color": "#F38181", "icon": "shield", "workload": 8, "status": "active", "sub_agents": 4},
    {"id": "dept-006", "name": "KAMADEVA", "description": "Customer Relations & Satisfaction", "deity": "Lord Kamadeva", "color": "#AA96DA", "icon": "heart", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-007", "name": "KUBERA", "description": "Asset Management & Resources", "deity": "Lord Kubera", "color": "#FCBAD3", "icon": "database", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-008", "name": "LAKSHMI", "description": "Revenue & Financial Operations", "deity": "Goddess Lakshmi", "color": "#F9ED69", "icon": "dollar-sign", "workload": 7, "status": "active", "sub_agents": 4},
    {"id": "dept-009", "name": "BRIHASPATI", "description": "Strategic Planning & Wisdom", "deity": "Lord Brihaspati", "color": "#B8E994", "icon": "lightbulb", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-010", "name": "SARASWATI", "description": "Learning, Training & Knowledge", "deity": "Goddess Saraswati", "color": "#78E08F", "icon": "book", "workload": 4, "status": "active", "sub_agents": 3},
    {"id": "dept-011", "name": "HANUMAN", "description": "Emergency Response & Swift Action", "deity": "Lord Hanuman", "color": "#FC5C65", "icon": "zap", "workload": 9, "status": "active", "sub_agents": 4},
    {"id": "dept-012", "name": "INDRA", "description": "Weather & Environmental Analysis", "deity": "Lord Indra", "color": "#45AAF2", "icon": "cloud", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-013", "name": "VAYU", "description": "Logistics & Fleet Management", "deity": "Lord Vayu", "color": "#A3CB38", "icon": "truck", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-014", "name": "AGNI", "description": "Power Grid & Energy Optimization", "deity": "Lord Agni", "color": "#FF7F50", "icon": "flame", "workload": 8, "status": "active", "sub_agents": 4},
    {"id": "dept-015", "name": "VARUNA", "description": "Water Resources & Cooling Systems", "deity": "Lord Varuna", "color": "#70A1FF", "icon": "droplet", "workload": 4, "status": "active", "sub_agents": 2},
    {"id": "dept-016", "name": "YAMA", "description": "Compliance & Regulatory Affairs", "deity": "Lord Yama", "color": "#5F27CD", "icon": "scale", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-017", "name": "VISHNU", "description": "System Stability & Maintenance", "deity": "Lord Vishnu", "color": "#0ABDE3", "icon": "settings", "workload": 7, "status": "active", "sub_agents": 4},
    {"id": "dept-018", "name": "BRAHMA", "description": "Innovation & New Initiatives", "deity": "Lord Brahma", "color": "#F8B739", "icon": "sparkles", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-019", "name": "DURGA", "description": "Crisis Management & Protection", "deity": "Goddess Durga", "color": "#E74C3C", "icon": "alert-triangle", "workload": 7, "status": "active", "sub_agents": 3},
    {"id": "dept-020", "name": "NARADA", "description": "Communications & Messaging", "deity": "Sage Narada", "color": "#9B59B6", "icon": "message-circle", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-021", "name": "PRAJAPATI", "description": "Creator & Builder - Project Management", "deity": "Lord Prajapati", "color": "#E67E22", "icon": "hammer", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-022", "name": "SHIV", "description": "Transformation & Auto-Rectification", "deity": "Lord Shiva", "color": "#3498DB", "icon": "refresh-cw", "workload": 8, "status": "active", "sub_agents": 4},
    {"id": "dept-023", "name": "PARVATI", "description": "Harmony & Workload Balance", "deity": "Goddess Parvati", "color": "#E91E63", "icon": "balance-scale", "workload": 5, "status": "active", "sub_agents": 3},
    {"id": "dept-024", "name": "CHITRAGUPTA", "description": "Records & Documentation", "deity": "Lord Chitragupta", "color": "#607D8B", "icon": "file-text", "workload": 4, "status": "active", "sub_agents": 2},
    {"id": "dept-025", "name": "ASHWINI KUMARAS", "description": "Health Monitoring & Diagnostics", "deity": "Ashwini Kumaras", "color": "#00BCD4", "icon": "activity", "workload": 6, "status": "active", "sub_agents": 3},
    {"id": "dept-026", "name": "DHANVANTARI", "description": "System Health & Recovery", "deity": "Lord Dhanvantari", "color": "#4CAF50", "icon": "heart-pulse", "workload": 7, "status": "active", "sub_agents": 3},
    {"id": "dept-027", "name": "KALI", "description": "Destruction of Errors & Bugs", "deity": "Goddess Kali", "color": "#212121", "icon": "x-circle", "workload": 9, "status": "active", "sub_agents": 4}
]

async def seed_database(db):
    """Seed the database with initial data if empty
    
    This is designed to handle permission-restricted environments like Atlas.
    If the user doesn't have permissions, seeding is gracefully skipped.
    """
    
    try:
        # Check if users collection is empty
        user_count = await db.users.count_documents({})
        if user_count == 0:
            logger.info("Seeding admin user...")
            # Hash the default password
            DEFAULT_ADMIN["hashed_password"] = pwd_context.hash("Kailash@2026")
            await db.users.insert_one(DEFAULT_ADMIN)
            logger.info(f"Admin user created: {DEFAULT_ADMIN['kailash_code']}")
        else:
            logger.info(f"Users already exist ({user_count} found), skipping user seeding")
            
            # Check if the specific user exists, if not add them
            existing_user = await db.users.find_one({"kailash_code": "KAILASH001"})
            if not existing_user:
                logger.info("Adding default admin user...")
                DEFAULT_ADMIN["hashed_password"] = pwd_context.hash("Kailash@2026")
                await db.users.insert_one(DEFAULT_ADMIN)
                logger.info(f"Admin user added: {DEFAULT_ADMIN['kailash_code']}")
        
        # Check if departments collection is empty
        dept_count = await db.departments.count_documents({})
        if dept_count == 0:
            logger.info("Seeding 27 AI departments...")
            for dept in DEPARTMENTS:
                dept["created_at"] = datetime.utcnow()
                dept["updated_at"] = datetime.utcnow()
            await db.departments.insert_many(DEPARTMENTS)
            logger.info(f"{len(DEPARTMENTS)} departments created")
        else:
            logger.info(f"Departments already exist ({dept_count} found), checking for missing departments...")
            # Add missing departments
            existing_names = await db.departments.distinct("name")
            missing_depts = [d for d in DEPARTMENTS if d["name"] not in existing_names]
            if missing_depts:
                logger.info(f"Adding {len(missing_depts)} missing departments: {[d['name'] for d in missing_depts]}")
                for dept in missing_depts:
                    dept["created_at"] = datetime.utcnow()
                    dept["updated_at"] = datetime.utcnow()
                await db.departments.insert_many(missing_depts)
                logger.info(f"✅ Added {len(missing_depts)} missing departments")
            else:
                logger.info("All departments already exist")
        
        # Ensure indexes exist
        try:
            await db.users.create_index("kailash_code", unique=True)
            await db.users.create_index("email", unique=True)
            await db.departments.create_index("name")
            logger.info("Database indexes created")
        except Exception as e:
            logger.info(f"Index creation skipped (may already exist): {e}")
            
    except Exception as e:
        error_str = str(e).lower()
        if "not authorized" in error_str or "unauthorized" in error_str:
            logger.warning(f"Database seeding skipped due to permissions: {str(e)[:100]}")
        else:
            logger.warning(f"Database seeding error: {e}")

async def run_seeder(mongo_url: str, database_name: str):
    """Run the seeder with given connection details"""
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[database_name]
        
        # Verify connection
        await client.admin.command('ping')
        logger.info(f"📡 Connected to MongoDB database: {database_name}")
        
        # Run seeding
        await seed_database(db)
        
        client.close()
        logger.info("✅ Database seeding completed")
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise

if __name__ == "__main__":
    # For manual testing
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DATABASE_NAME", "kailash")
    
    asyncio.run(run_seeder(mongo_url, db_name))
