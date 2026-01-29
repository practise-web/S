import logging
from fastapi import FastAPI, APIRouter
from app.routers.v1 import auth, doc, user
from app.core.security import setup_middlewares
from app.core.logger import configure_logging, LogLevels
from app.core.rate_limiter import limiter


configure_logging(LogLevels.info)
logger = logging.getLogger("app")
logger.info("Starting ScholarMind application")


app = FastAPI(
    title="ScholarMind",
    version="1.0.0",
    description="An AI-powered platform to assist students with their academic needs.",
    root_path="/api",
    docs_url="/",
)
app.state.limiter = limiter
setup_middlewares(app)

# --- VERSION 1 SETUP ---
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth.router)
v1_router.include_router(user.router)
v1_router.include_router(doc.router)

app.include_router(v1_router)
# if(__name__ == "__main__"):
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)