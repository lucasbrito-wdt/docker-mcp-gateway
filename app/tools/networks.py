import json
from docker_client import get_client


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def list_networks(args: dict) -> dict:
    try:
        client = get_client()
        networks = client.networks.list()
        result = [
            {
                "id": net.short_id,
                "name": net.name,
                "driver": net.attrs.get("Driver", ""),
            }
            for net in networks
        ]
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def create_network(args: dict) -> dict:
    try:
        name = args.get("name")
        if not name:
            return _err("'name' is required")

        driver = args.get("driver", "bridge")
        client = get_client()
        network = client.networks.create(name=name, driver=driver)
        return _ok(json.dumps({"id": network.short_id, "name": network.name}))
    except Exception as e:
        return _err(str(e))


def remove_network(args: dict) -> dict:
    try:
        network_id = args.get("id") or args.get("name")
        if not network_id:
            return _err("'id' or 'name' is required")

        client = get_client()
        network = client.networks.get(network_id)
        network.remove()
        return _ok(f"Network {network_id} removed")
    except Exception as e:
        return _err(str(e))
