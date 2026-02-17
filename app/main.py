from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints import extract, health

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("santa-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("santa-ai starting up on %s:%s", settings.HOST, settings.PORT)
    yield
    logger.info("santa-ai shutting down")


app = FastAPI(
    title="santa-ai",
    description="Document extraction microservice",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(extract.router)
