"""
ZooKeeper client service for interacting with ZooKeeper
"""

import logging
import json
from typing import Dict, List, Tuple, Union, Optional, Any
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from zookeeper_rest_proxy.config.settings import settings

logger = logging.getLogger(__name__)

# Global ZooKeeper client
_zk_client = None


def get_zk_client() -> KazooClient:
    """
    Get or create the ZooKeeper client

    Returns:
        KazooClient: The global ZooKeeper client instance
    """
    global _zk_client

    if _zk_client is None:
        logger.info(f"Connecting to ZooKeeper at {settings.ZK_HOSTS}")
        _zk_client = KazooClient(
            hosts=settings.ZK_HOSTS,
            timeout=settings.ZK_TIMEOUT,
            read_only=settings.ZK_READ_ONLY,
        )

        def connection_listener(state):
            if state == KazooState.LOST:
                logger.warning("ZooKeeper connection lost")
            elif state == KazooState.SUSPENDED:
                logger.warning("ZooKeeper connection suspended")
            else:
                logger.info("ZooKeeper connected")

        _zk_client.add_listener(connection_listener)
        _zk_client.start()

    return _zk_client


def close_zk_client():
    """Close the ZooKeeper client connection"""
    global _zk_client
    if _zk_client is not None:
        logger.info("Closing ZooKeeper connection")
        _zk_client.stop()
        _zk_client.close()
        _zk_client = None


class ZooKeeperService:
    """Service for interacting with ZooKeeper"""

    @staticmethod
    def get_children(path: str) -> List[str]:
        """
        Get children of a ZooKeeper path

        Args:
            path (str): ZooKeeper path

        Returns:
            List[str]: List of child node names

        Raises:
            NoNodeError: If the path does not exist
        """
        zk = get_zk_client()
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"

        return zk.get_children(path)

    @staticmethod
    def get_data(
        path: str,
    ) -> Tuple[Optional[Union[Dict[str, Any], str]], Dict[str, Any]]:
        """
        Get data from a ZooKeeper path

        Args:
            path (str): ZooKeeper path

        Returns:
            Tuple[Any, Dict]: (decoded data, node stats)

        Raises:
            NoNodeError: If the path does not exist
        """
        zk = get_zk_client()
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"

        data, stat = zk.get(path)

        decoded_data = None
        if data:
            try:
                text_data = data.decode("utf-8")
                try:
                    decoded_data = json.loads(text_data)
                except json.JSONDecodeError:
                    decoded_data = text_data
            except UnicodeDecodeError:
                import base64

                decoded_data = {
                    "_binary": True,
                    "data_base64": base64.b64encode(data).decode("ascii"),
                }

        stat_info = {
            "created": stat.created,
            "modified": stat.mtime,
            "version": stat.version,
            "children_count": stat.children_count,
            "ephemeral_owner": stat.ephemeralOwner,
            "data_length": stat.dataLength,
        }

        return decoded_data, stat_info

    @staticmethod
    def exists(path: str) -> Optional[Dict[str, Any]]:
        """
        Check if a path exists in ZooKeeper

        Args:
            path (str): ZooKeeper path

        Returns:
            Optional[Dict]: Stat info if exists, None otherwise
        """
        zk = get_zk_client()
        if not path.startswith("/"):
            path = f"/{path}"

        stat = zk.exists(path)
        if stat:
            return {
                "created": stat.created,
                "modified": stat.mtime,
                "version": stat.version,
                "children_count": stat.children_count,
                "ephemeral_owner": stat.ephemeralOwner,
                "data_length": stat.dataLength,
            }
        return None

    @staticmethod
    def create(
        path: str,
        data: Union[str, Dict[str, Any], bytes] = None,
        ephemeral: bool = False,
        sequence: bool = False,
        makepath: bool = True,
    ) -> str:
        """
        Create a node in ZooKeeper

        Args:
            path (str): ZooKeeper path
            data (Union[str, Dict, bytes], optional): Data to store
            ephemeral (bool, optional): Whether node is ephemeral
            sequence (bool, optional): Whether node name is sequential
            makepath (bool, optional): Create parent nodes if needed

        Returns:
            str: Path of created node

        Raises:
            NodeExistsError: If the node already exists
        """
        zk = get_zk_client()
        if not path.startswith("/"):
            path = f"/{path}"

        # Prepare data
        if data is None:
            data_bytes = b""
        elif isinstance(data, bytes):
            data_bytes = data
        elif isinstance(data, dict):
            data_bytes = json.dumps(data).encode("utf-8")
        else:
            data_bytes = str(data).encode("utf-8")

        return zk.create(
            path, data_bytes, ephemeral=ephemeral, sequence=sequence, makepath=makepath
        )

    @staticmethod
    def set(path: str, data: Union[str, Dict[str, Any], bytes]) -> Dict[str, Any]:
        """
        Set data for a ZooKeeper node

        Args:
            path (str): ZooKeeper path
            data (Union[str, Dict, bytes]): Data to store

        Returns:
            Dict: Stat info after update

        Raises:
            NoNodeError: If the node does not exist
        """
        zk = get_zk_client()
        if not path.startswith("/"):
            path = f"/{path}"

        if isinstance(data, bytes):
            data_bytes = data
        elif isinstance(data, dict):
            data_bytes = json.dumps(data).encode("utf-8")
        else:
            data_bytes = str(data).encode("utf-8")

        stat = zk.set(path, data_bytes)

        return {
            "created": stat.created,
            "modified": stat.mtime,
            "version": stat.version,
            "children_count": stat.children_count,
            "ephemeral_owner": stat.ephemeralOwner,
            "data_length": stat.dataLength,
        }

    @staticmethod
    def delete(path: str, recursive: bool = False) -> bool:
        """
        Delete a ZooKeeper node

        Args:
            path (str): ZooKeeper path
            recursive (bool, optional): Delete recursively

        Returns:
            bool: True if deleted

        Raises:
            NoNodeError: If the node does not exist
        """
        zk = get_zk_client()
        if not path.startswith("/"):
            path = f"/{path}"

        if recursive:
            zk.delete(path, recursive=True)
        else:
            zk.delete(path)

        return True
