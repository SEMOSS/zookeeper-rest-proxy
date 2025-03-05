import logging
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, Union

from zookeeper_rest_proxy.services.zookeeper import ZooKeeperService
from zookeeper_rest_proxy.models.models import NodeDataResponse, NodeChildrenResponse

logger = logging.getLogger(__name__)
zk_route = APIRouter(tags=["ZooKeeper"])


@zk_route.get(
    "/znodes/v1",
    response_model=NodeChildrenResponse,
    summary="Get root nodes",
    description="Retrieve the children of the root node in ZooKeeper",
)
async def get_root_nodes():
    """Get root nodes"""
    try:
        children = ZooKeeperService.get_children("/")
        return NodeChildrenResponse(path="/", children=children, count=len(children))
    except Exception as e:
        logger.error(f"Error getting root nodes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting root nodes: {str(e)}"
        )


@zk_route.get(
    "/znodes/v1/{path:path}",
    response_model=Union[NodeDataResponse, NodeChildrenResponse],
    summary="Get node data or children",
    description="Retrieve node data or children based on the view parameter",
)
async def get_node(
    path: str = Path(..., description="ZooKeeper path"),
    view: Optional[str] = Query(None, description="View type (children or data)"),
):
    """Get node data or children"""
    if not path.startswith("/"):
        path = f"/{path}"

    try:
        stat_info = ZooKeeperService.exists(path)
        if not stat_info:
            raise HTTPException(status_code=404, detail=f"Node {path} not found")

        if view == "children":
            children = ZooKeeperService.get_children(path)
            return NodeChildrenResponse(
                path=path, children=children, count=len(children)
            )

        data, stat = ZooKeeperService.get_data(path)

        return NodeDataResponse(path=path, exists=True, data=data, stat=stat)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error getting node {path}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting node: {str(e)}")


@zk_route.head(
    "/znodes/v1/{path:path}",
    summary="Check if node exists",
    description="Check if a node exists in ZooKeeper",
)
async def check_node_exists(path: str = Path(..., description="ZooKeeper path")):
    """Check if node exists (HEAD method)"""
    if not path.startswith("/"):
        path = f"/{path}"

    try:
        exists = ZooKeeperService.exists(path)
        if not exists:
            raise HTTPException(status_code=404, detail=f"Node {path} not found")

        return {}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error checking if node {path} exists: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking node: {str(e)}")
