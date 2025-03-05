from fastapi import APIRouter
from zookeeper_rest_proxy.services.zookeeper import get_zk_client

health_route = APIRouter()


@health_route.get("/health")
async def health():
    """Health check endpoint"""
    zk_client = get_zk_client()
    if zk_client and zk_client.connected:
        return {"status": "ok", "zookeeper_connected": True}
    return {"status": "degraded", "zookeeper_connected": False}
