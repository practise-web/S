from fastapi import FastAPI, APIRouter
from app.routers.v1 import auth, user
from app.core.middleware import (
    PhantomTokenMiddleware,
    RequestIdMiddleware,
    LoggingMiddleware,
)
from app.core.logger import configure_logging, LogLevels
from app.core.rate_limiter import limiter
from app.core.config import redis_settings
from app.core import network as net
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from app.core import database as db
import redis.asyncio as redis
import logging
import httpx
from dotenv import load_dotenv

configure_logging(LogLevels.info)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing resources")
    load_dotenv()
    # Initialize resources here (e.g., database connections, caches)
    logger.info(f"Connecting to Redis at {redis_settings.redis_url}")
    db.redis_client = redis.from_url(
        str(redis_settings.redis_url), decode_responses=True
    )
    logger.info("Redis connection established")
    net.client = httpx.AsyncClient(timeout=30.0)
    logger.info("Global HTTP Client initialized with 30s timeout.")
    logger.info("Resources initialized successfully")

    yield

    # Clean up resources here (e.g., close database connections, flush caches)
    logger.info("Application shutdown: Cleaning up resources")
    await db.redis_client.close()
    logger.info("Redis connection closed")
    if net.client:
        await net.client.aclose()
        logger.info("HTTP client closed")
    logger.info("Resources cleaned up successfully")


app = FastAPI(
    title="ScholarMind",
    version="1.0.0",
    description="An AI-powered platform to assist students with their academic needs.",
    root_path="/api",
    docs_url="/",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(PhantomTokenMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # which origins can access
    allow_credentials=True,  # allow cookies/auth headers
    allow_methods=["*"],  # GET, POST, PUT, etc.
    allow_headers=["*"],  # allow custom headers
)


# --- VERSION 1 SETUP ---
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth.router)
v1_router.include_router(user.router)
# v1_router.include_router(doc.router)

app.include_router(v1_router)
# if(__name__ == "__main__"):
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
