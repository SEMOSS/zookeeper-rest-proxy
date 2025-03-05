# Zookeeper REST Proxy
RESTful API for interacting with Apache ZooKeeper

## Installation
- `poetry env activate`
- `poetry install`

## Usage
- `poetry run zk-proxy`
- `http://localhost:8000/docs`

## Docker
- `docker build -t zk-proxy .`
- `docker run -p 8000:8000 zk-proxy`

## Endpoints
- `GET api/health`: Check if server is running & connected to ZooKeeper
- `GET api/znode/v1`: Get root nodes
- `GET api/znode/{path}`: Get node data or children
- `HEAD api/znode/{path}`: Check if node exists
