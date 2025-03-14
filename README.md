# Zookeeper REST Proxy
RESTful API for interacting with Apache ZooKeeper

## Installation
- `uv pip install .`

## Usage
- `zk-proxy`

## Docker
- `docker build -t zk-proxy .`
- `docker run -p 8989:8989 zk-proxy`

## Endpoints
- `GET /health`: Check if server is running & connected to ZooKeeper
- `GET /znode/v1`: Get root nodes
- `GET /znode/{path}`: Get node data or children
- `HEAD /znode/{path}`: Check if node exists
