from backend.shared import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "rag"
    version: str = "0.1.0"


settings = Settings()
