import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file explicitly
load_dotenv()

def extract_db_name_from_mongo_url(mongo_url: str, default_name: str = "kailash") -> str:
    """
    Extract database name from MongoDB connection string.
    For Atlas: mongodb+srv://user:pass@cluster.mongodb.net/dbname?options
    For local: mongodb://localhost:27017/dbname

    IMPORTANT: For Emergent deployment Atlas connections, users typically have
    permissions on a specific database (like 'kailash'), NOT on 'test'.
    Always default to 'kailash' unless explicitly specified in URL.
    """
    if not mongo_url:
        return default_name

    try:
        # Parse the URL - handle mongodb+srv:// scheme
        url_to_parse = mongo_url
        if mongo_url.startswith('mongodb+srv://'):
            url_to_parse = mongo_url.replace('mongodb+srv://', 'https://')
        elif mongo_url.startswith('mongodb://'):
            url_to_parse = mongo_url.replace('mongodb://', 'https://')

        parsed = urlparse(url_to_parse)

        # Get the path (database name) - remove leading slash
        path = parsed.path.lstrip('/')

        # If path has database name (and it's not empty or just query params)
        if path and '?' not in path:
            return path
        elif path and '?' in path:
            db_name = path.split('?')[0]
            if db_name:
                return db_name

        # No database specified in URL - use the default (kailash)
        # DO NOT use 'test' as Emergent users typically don't have 'test' permissions
        return default_name

    except Exception as e:
        print(f"[WARN] Error parsing MongoDB URL for database name: {e}")
        return default_name

# Get the MONGO_URL first
_mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

# Check if this is an Atlas/production deployment
_is_atlas = 'mongodb+srv' in _mongo_url or 'mongodb.net' in _mongo_url

# Determine database name:
# Priority:
# 1. DATABASE_NAME or DB_NAME environment variable
# 2. Database name from URL path
# 3. Default to 'kailash' (NOT 'test' - users don't have permissions)
_explicit_db_name = os.environ.get('DATABASE_NAME', os.environ.get('DB_NAME', None))
if _explicit_db_name:
    _database_name = _explicit_db_name
else:
    _database_name = extract_db_name_from_mongo_url(_mongo_url, "kailash")

# The development fallback for SECRET_KEY. It is published in this repository,
# so anything signed with it can be forged by anyone who has read the source.
# Startup rejects it when ENV names a production environment (TRD NFR-Sec4).
# secret-scan: allow the literal must be here to be rejected; it is the sentinel
DEV_SECRET_KEY = 'dev-secret-key-change-in-production'
PRODUCTION_ENVS = {'production', 'prod'}


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Kailash Backend"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENV: str = os.environ.get('ENV', 'dev')

    # MongoD Settings
    MONGO_URL: str = _mongo_url
    DATABASE_NAME: str = _database_name

    # JWT Settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY', DEV_SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS Settings
    CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')

    # OpenAI Settings (for GANESHA AI)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"  # Will be updated to GPT-5 once available

    # Emergent LLM Key
    EMERGENT_LLM_KEY: str | None = None

    # GANESHA Orchestrator - Claude API (direct Anthropic)
    anthropic_api_key: str = os.environ.get('ANTHROPIC_API_KEY', 'sk-ant-placeholder-will-be-added-by-user')

    # OpenRouter (OpenAI-compatible gateway; preferred if set)
    openrouter_api_key: str | None = os.environ.get('OPENROUTER_API_KEY', None)
    openrouter_base_url: str = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    openrouter_model: str = os.environ.get('OPENROUTER_MODEL', 'anthropic/claude-3-haiku')
    openrouter_site_url: str | None = os.environ.get('OPENROUTER_SITE_URL', 'https://kailash-ai.in')
    openrouter_app_name: str = os.environ.get('OPENROUTER_APP_NAME', 'Kailash')

    # Emergent Platform (for future integration)
    emergent_api_url: str | None = os.environ.get('EMERGENT_API_URL', None)
    emergent_api_key: str | None = os.environ.get('EMERGENT_API_KEY', None)
    emergent_project_id: str | None = os.environ.get('EMERGENT_PROJECT_ID', 'KAILASH-hub')

    # Domain Configuration
    backend_url: str | None = os.environ.get('BACKEND_URL', None)
    frontend_url: str | None = os.environ.get('FRONTEND_URL', None)
    allowed_origins: str | None = os.environ.get('ALLOWED_ORIGINS', None)

    # GST Software Integration (Automobile Module)
    GST_SOFTWARE_API_URL: str = os.environ.get('GST_SOFTWARE_API_URL', '')
    GST_SOFTWARE_API_KEY: str = os.environ.get('GST_SOFTWARE_API_KEY', '')

    # Pinecone RAG Configuration
    PINECONE_API_KEY: str = os.environ.get('PINECONE_API_KEY', '')
    PINECONE_INDEX: str = os.environ.get('PINECONE_INDEX', 'kailashai')
    PINECONE_HOST: str = os.environ.get('PINECONE_HOST', 'us-east-1')

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()


def _reject_development_defaults(s: "Settings") -> None:
    """Fail fast when a development default reaches a production environment.

    TRD NFR-Sec4 and TR-2. This runs at import, so the process dies before it
    can accept a request signed with a key that is public knowledge.
    """
    if s.ENV.strip().lower() not in PRODUCTION_ENVS:
        return

    problems = []
    if s.SECRET_KEY == DEV_SECRET_KEY:
        problems.append(
            "SECRET_KEY is the development default published in this repository; "
            "any JWT signed with it can be forged. Set SECRET_KEY to a long random value."
        )
    if s.CORS_ORIGINS.strip() == "*":
        problems.append(
            "CORS_ORIGINS is '*'. Set it to an explicit comma-separated origin list."
        )
    if problems:
        raise RuntimeError(
            f"Refusing to start with ENV={s.ENV!r}:\n  - " + "\n  - ".join(problems)
        )


_reject_development_defaults(settings)


def get_settings():
    """Helper function to get settings instance"""
    return settings
