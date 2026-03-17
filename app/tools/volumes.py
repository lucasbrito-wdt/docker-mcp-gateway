import json
from ..docker_client import get_client


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def list_volumes(args: dict) -> dict:
    try:
        client = get_client()
        volumes = client.volumes.list()
        result = [
            {
                "name": vol.name,
                "driver": vol.attrs.get("Driver", ""),
                "mountpoint": vol.attrs.get("Mountpoint", ""),
            }
            for vol in volumes
        ]
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def create_volume(args: dict) -> dict:
    try:
        name = args.get("name")
        if not name:
            return _err("'name' is required")

        driver = args.get("driver", "local")
        client = get_client()
        volume = client.volumes.create(name=name, driver=driver)
        return _ok(json.dumps({"name": volume.name, "driver": volume.attrs.get("Driver", "")}))
    except Exception as e:
        return _err(str(e))


def remove_volume(args: dict) -> dict:
    try:
        name = args.get("name")
        if not name:
            return _err("'name' is required")

        client = get_client()
        volume = client.volumes.get(name)
        volume.remove()
        return _ok(f"Volume {name} removed")
    except Exception as e:
        return _err(str(e))
