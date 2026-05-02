from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
import asyncio
import os
from datetime import datetime

from .core.config import settings
from .core.mongodb import MongoD
from .core.database import db_manager
from .core.db_indexes import create_indexes
from .core.seeder import seed_database
from .core.firebase import init_firebase
from .middleware.security import security_middleware
from .middleware.error_handler import error_handler
from .api import auth, departments, tasks, ganesha, analytics, ganesha_orchestrator, simple_health, guardians, conversations, rbac, users
from .api import ganesha_multimodel, shiv_auto_rectify, dashboard, ganesha_v2, system_health
from .core.performance import performance_monitoring_task

logger = logging.getLogger("kailash")

# Import v2 router - try multiple import paths for compatibility
ganesha_v2_router = None
try:
    from backend.routers.v2 import ganesha_router as ganesha_v2_router
except ImportError:
    try:
        from .routers.v2 import ganesha_router as ganesha_v2_router
    except ImportError:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from routers.v2 import ganesha_router as ganesha_v2_router
        except ImportError:
            logger.warning("⚠️ GANESHA v2 router not available - v2 endpoints disabled")

from .automobile import router as automobile_router

async def validate_database_permissions():
    """Validate MongoDB Atlas permissions on critical collections
    
    This check ensures that the Atlas user has necessary permissions before the app
    accepts traffic. Without read access on 'users' collection, authentication will fail.
    """
    try:
        db = MongoD.get_database()
        
        # Check if we're in a permission-restricted environment
        permission_check_enabled = os.getenv("SKIP_PERMISSION_CHECK", "false").lower() != "true"
        
        if not permission_check_enabled:
            # Silently skip permission check when disabled
            return
        
        # Test read permission on users collection (CRITICAL)
        try:
            await db.users.find_one({}, {"_id": 1})
            logger.info("✅ Database permissions validated: users collection accessible")
        except Exception as e:
            error_str = str(e).lower()
            if "not authorized" in error_str or "unauthorized" in error_str or (hasattr(e, 'code') and e.code == 13):
                logger.critical("")
                logger.critical("=" * 80)
                logger.critical("❌ DEPLOYMENT BLOCKER: MongoDB Atlas Permission Denied")
                logger.critical("=" * 80)
                logger.critical("")
                logger.critical("ERROR: Cannot read 'users' collection in 'kailash' database")
                logger.critical("USER: kailash-mgmt")
                logger.critical("DATABASE: kailash")
                logger.critical("")
                logger.critical("IMPACT:")
                logger.critical("  - Authentication system will NOT work")
                logger.critical("  - All login attempts will return 500 errors")
                logger.critical("  - Application is NOT functional")
                logger.critical("")
                logger.critical("FIX REQUIRED:")
                logger.critical("  1. Open MongoDB Atlas Console")
                logger.critical("  2. Go to Database Access")
                logger.critical("  3. Find user 'kailash-mgmt'")
                logger.critical("  4. Grant 'readWrite' role on database 'kailash'")
                logger.critical("")
                logger.critical("ALTERNATIVE (Testing Only):")
                logger.critical("  Set environment variable: SKIP_PERMISSION_CHECK=true")
                logger.critical("  WARNING: This will allow startup but authentication will still fail")
                logger.critical("")
                logger.critical("=" * 80)
                logger.critical("")
                
                # In production, this should fail startup
                # But we'll allow it to continue for now with clear warnings
                # Uncomment the line below to make it fail hard:
                # raise RuntimeError("Database permission error - authentication will not work")
                
            else:
                raise
        
        # Test write permission (NICE TO HAVE)
        try:
            test_doc = {"check": "startup_permission_test", "timestamp": datetime.utcnow()}
            await db.system_health.insert_one(test_doc)
            await db.system_health.delete_one({"check": "startup_permission_test"})
            logger.info("✅ Database permissions validated: write access confirmed")
        except Exception as e:
            if "not authorized" in str(e).lower():
                logger.warning("⚠️ Database WRITE permissions limited - some features may not work")
                logger.warning("   CRUD operations on collections may fail")
                
    except Exception as e:
        logger.error(f"Permission validation error: {str(e)}")
        logger.warning("⚠️ Continuing startup - but database operations may fail")

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(" Starting Kailash...")
    logger.info("Environment: Production | Domain: kailash-ai.in")
    logger.info("Company: Go4Garage - URGAA EV Charging")
    
    startup_tasks = []
    
    try:
        # MongoDB connection with extended timeout for Atlas
        logger.info("Connecting to MongoDB...")
        await asyncio.wait_for(MongoD.connect_db(), timeout=15.0)
        logger.info("✅ MongoDB connected")
        
        # Database seeding (non-blocking)
        try:
            db = MongoD.get_database()
            await asyncio.wait_for(seed_database(db), timeout=10.0)
            logger.info("✅ Database seeded")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Database seeding timeout - continuing")
        except Exception as seed_error:
            logger.warning(f"⚠️ Database seeding skipped: {seed_error}")
        
        # Validate database permissions (critical for production)
        try:
            await asyncio.wait_for(validate_database_permissions(), timeout=8.0)
        except asyncio.TimeoutError:
            logger.warning("⚠️ Permission validation timeout")
        
        # Create database indexes (non-blocking)
        try:
            await asyncio.wait_for(create_indexes(), timeout=15.0)
            logger.info("✅ Database indexes created")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Index creation timeout - will create lazily")
        except Exception as idx_error:
            logger.warning(f"⚠️ Index creation failed: {idx_error}")
        
        # Additional database connections (optional)
        try:
            await asyncio.wait_for(db_manager.connect_all(), timeout=8.0)
            logger.info("✅ All databases connected")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Additional database connections timeout")
        except Exception as e:
            logger.warning(f"⚠️ Additional databases connection failed: {e}")
        
        # Start background performance monitoring
        asyncio.create_task(performance_monitoring_task())
        logger.info("✅ Performance monitoring started")
        
        # Initialize Firebase Admin SDK
        try:
            init_firebase()
        except Exception as fb_err:
            logger.warning(f"⚠️ Firebase init skipped: {fb_err}")
        
        logger.info("✅ KAILASH started successfully")
        
    except asyncio.TimeoutError:
        logger.error("❌ MongoDB connection timeout - continuing in degraded mode")
        logger.warning("⚠️ Application will continue without database")
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)} - continuing in degraded mode")
        logger.warning("⚠️ Application will continue with limited functionality")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down KAILASH...")
    try:
        await MongoD.close_db()
        await db_manager.close_all()
        logger.info("✅ KAILASH shutdown complete")
    except Exception as e:
        logger.error(f"⚠️ Shutdown error: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
_cors_origins = ["*"]
_allow_credentials = False
if settings.allowed_origins:
    _cors_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    _allow_credentials = True
elif settings.frontend_url:
    _cors_origins = [settings.frontend_url, "http://localhost:3000"]
    _allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# === PRODUCTION SECURITY MIDDLEWARE === None
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await security_middleware.add_security_headers(request, call_next)
    # orce override Server header by rebuilding raw headers
    response.raw_headers = [
        (k, v) for k, v in response.raw_headers 
        if k.lower() != b"server"
    ]
    response.raw_headers.append((b"server", b"KAILASH/."))
    return response

@app.middleware("http")
async def check_rate_limit(request: Request, call_next):
    """Rate limiting middleware - skip for health checks"""
    if request.url.path in ["/api/health", "/health", "/"]:
        return await call_next(request)
    
    await security_middleware.rate_limit_check(request)
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    error_handler.log_request(request, duration, response.status_code)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await error_handler.handle_exception(request, exc)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(ganesha.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(ganesha_orchestrator.router, prefix="/api", tags=["GANESHA Orchestrator"])
app.include_router(guardians.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(rbac.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(automobile_router, prefix="/api")
app.include_router(ganesha_multimodel.router, prefix="/api", tags=["GANESHA Multi-Model AI"])
app.include_router(shiv_auto_rectify.router, prefix="/api", tags=["SHIV Auto-Rectification"])
app.include_router(dashboard.router, prefix="/api", tags=["Executive Dashboard"])
app.include_router(ganesha_v2.router, prefix="/api", tags=["GANESHA v2.0 with RAG"])
if ganesha_v2_router:
    app.include_router(ganesha_v2_router, prefix="/api/v2", tags=["GANESHA v2.0 Analytics"])
app.include_router(system_health.router, tags=["System Health"])
app.include_router(simple_health.router, tags=["Health"])

# Health check endpoint
@app.get("/api/health")
@app.head("/api/health")
@app.get("/health")
@app.head("/health")
async def health_check():
    """Production health check for Kubernetes probes - Always returns  for readiness"""
    try:
        # Check if MongoD client exists and is connected
        db_healthy = False
        if MongoD.client is not None:
            try:
                # Quick ping to verify connection without blocking
                await asyncio.wait_for(
                    MongoD.client.admin.command('ping'),
                    timeout=1.0
                )
                db_healthy = True
            except:
                db_healthy = False
        
        # Always return 200 OK for Kubernetes probes, even if DB is not ready
        # This prevents pod restarts during startup
        return {
            "status": "healthy",  # Always healthy for k8s probes
            "app": "Kailash",  # Application name
            "database": "connected" if db_healthy else "initializing",
            "timestamp": datetime.now().isoformat(),
            "version": settings.VERSION,
            "company": "Go4Garage",
            "product": "Kailash",
            "domain": "kailash-ai.in",
            "departments": 20,
            "sub_agents": 64
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        # Still return 200 OK to prevent Kubernetes from killing the pod
        return {
            "status": "healthy",
            "database": "initializing",
            "timestamp": datetime.now().isoformat(),
            "version": settings.VERSION,
            "error": "Database connection in progress"
        }

@app.get("/api/security/stats")
async def security_stats():
    """Get security statistics for monitoring"""
    return security_middleware.get_security_stats()

# Swagger/OpenAPI endpoint aliases for deployment health checks
@app.get("/api/swagger.json")
@app.get("/api-docs/swagger.json")
async def swagger_json_alias():
    """Alias for OpenAPI JSON - redirects to standard OpenAPI endpoint"""
    from fastapi.openapi.utils import get_openapi
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

# GraphQL endpoint stubs (app is REST-only, return proper message)
@app.get("/api/graphql")
@app.post("/api/graphql")
@app.get("/api/gql")
@app.post("/api/gql")
async def graphql_not_supported():
    """GraphQL not implemented - this is a REST API"""
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not Implemented",
            "message": "This API uses REST, not GraphQL. Please refer to /api/docs for available endpoints.",
            "docs": "/api/docs"
        }
    )

@app.get("/api/")
@app.post("/api/")
@app.get("/")
async def root():
    """Root endpoint - supports GET and POST for health checks"""
    return {
        "message": "Kailash API",
        "company": "Go4Garage",
        "product": "URGAA - EV Charging Network",
        "domain": "kailash-ai.in",
        "version": settings.VERSION,
        "documentation": "/api/docs",
        "health": "/api/health",
        "openapi": "/api/openapi.json",
        "swagger": "/api/swagger.json",
        "departments": 20,
        "theme": {
            "primary": "#0A3D62",  # G4G Blue
            "accent": "#FFC312"    # Electric Yellow
        }
    }
