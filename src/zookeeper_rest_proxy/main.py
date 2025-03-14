import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from zookeeper_rest_proxy.routes.health_route import health_route
from zookeeper_rest_proxy.routes.zk_route import zk_route
from zookeeper_rest_proxy.services.zookeeper import get_zk_client, close_zk_client
from zookeeper_rest_proxy.config.settings import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info("Starting ZooKeeper REST Proxy")
    get_zk_client()

    yield

    logger.info("Shutting down ZooKeeper REST Proxy")
    close_zk_client()


app = FastAPI(
    title="ZooKeeper REST Proxy",
    description="RESTful API for interacting with Apache ZooKeeper",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_route)
app.include_router(zk_route)


@app.get("/")
async def root():
    """Root endpoint providing service information"""
    return {
        "name": "ZooKeeper REST Proxy",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


def start():
    """Entry point for the application"""
    uvicorn.run(
        "zookeeper_rest_proxy.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    start()
