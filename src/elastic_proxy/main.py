from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import complex, generic, predefined

app = FastAPI(
    title="Elasticsearch Proxy API",
    description="Proxy HTTP pour Elasticsearch 8/9",
    version="1.0.0",
    docs_url="/swagger",  # URL personnalisée pour SwaggerUI
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(predefined.router)
app.include_router(complex.router)
app.include_router(generic.router)
