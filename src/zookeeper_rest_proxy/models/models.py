"""
Pydantic models for API requests and responses
"""

from typing import Dict, List, Union, Optional, Any
from pydantic import BaseModel, Field


class NodeDataRequest(BaseModel):
    """Request model for creating/updating node data"""

    data: Optional[Union[Dict[str, Any], str, List[Any]]] = Field(
        None, description="Data to store in the node"
    )
    ephemeral: bool = Field(False, description="Whether the node should be ephemeral")
    sequence: bool = Field(False, description="Whether the node should be sequential")


class StatInfo(BaseModel):
    """ZooKeeper node stat information"""

    created: float = Field(..., description="Creation time (milliseconds since epoch)")
    modified: float = Field(
        ..., description="Last modified time (milliseconds since epoch)"
    )
    version: int = Field(..., description="Data version")
    children_count: int = Field(..., description="Number of children")
    ephemeral_owner: int = Field(..., description="Session ID of ephemeral node owner")
    data_length: int = Field(..., description="Length of data in bytes")


class NodeExistsResponse(BaseModel):
    """Response for checking if a node exists"""

    exists: bool = Field(..., description="Whether the node exists")
    stat: Optional[StatInfo] = Field(
        None, description="Node stat information if exists"
    )


class NodeDataResponse(BaseModel):
    """Response for getting node data"""

    path: str = Field(..., description="ZooKeeper path")
    exists: bool = Field(..., description="Whether the node exists")
    data: Optional[Union[Dict[str, Any], str, List[Any]]] = Field(
        None, description="Node data (decoded)"
    )
    data_is_binary: bool = Field(
        False, description="Whether data was binary (non-UTF8)"
    )
    data_base64: Optional[str] = Field(
        None, description="Base64 encoded data if binary"
    )
    stat: Optional[StatInfo] = Field(None, description="Node stat information")


class NodeChildrenResponse(BaseModel):
    """Response for getting node children"""

    path: str = Field(..., description="ZooKeeper path")
    children: List[str] = Field(..., description="List of child node names")
    count: int = Field(..., description="Number of children")


class NodeCreateResponse(BaseModel):
    """Response for creating a node"""

    path: str = Field(..., description="Path of created node")
    success: bool = Field(True, description="Whether the operation was successful")


class NodeUpdateResponse(BaseModel):
    """Response for updating node data"""

    path: str = Field(..., description="ZooKeeper path")
    success: bool = Field(True, description="Whether the operation was successful")
    stat: StatInfo = Field(..., description="Node stat information after update")


class NodeDeleteResponse(BaseModel):
    """Response for deleting a node"""

    path: str = Field(..., description="ZooKeeper path")
    success: bool = Field(True, description="Whether the operation was successful")


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
    path: Optional[str] = Field(None, description="ZooKeeper path if relevant")
