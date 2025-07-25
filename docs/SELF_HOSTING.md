# Self-Hosting Guide

The Autonomy server can be deployed on-premise using Docker.

```bash
docker build -t autonomy .
docker run -p 8000:8000 autonomy
```

Ensure that the container has access to your GitHub credentials via environment
variables or mounted files. See [CONFIGURATION](CONFIGURATION.md) for details.
