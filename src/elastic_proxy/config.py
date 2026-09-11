import os
from typing import Optional


class Settings:
    # Elasticsearch
    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "http://localhost:9200")
    ELASTIC_USER: str = os.getenv("ELASTIC_USER", "elastic")
    ELASTIC_PASSWORD: str = os.getenv("ELASTIC_PASSWORD", "")
    ELASTIC_CERT_PATH: Optional[str] = os.getenv("ELASTIC_CERT_PATH")  # None si pas de certificat

    # Proxy
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")


settings = Settings()
