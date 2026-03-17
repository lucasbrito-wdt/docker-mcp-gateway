import docker

_client = None


def get_client():
    global _client
    if _client is None:
        _client = docker.from_env()
        try:
            _client.ping()
        except Exception as e:
            raise RuntimeError(f"Cannot connect to Docker socket: {e}")
    return _client
