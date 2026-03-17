import json
from docker_client import get_client


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def list_containers(args: dict) -> dict:
    try:
        client = get_client()
        containers = client.containers.list(all=True)
        result = [
            {
                "id": c.short_id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
            }
            for c in containers
        ]
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def create_container(args: dict) -> dict:
    try:
        image = args.get("image")
        if not image:
            return _err("'image' is required")

        client = get_client()
        container = client.containers.create(
            image=image,
            name=args.get("name"),
            command=args.get("command"),
            environment=args.get("environment"),
            ports=args.get("ports"),
        )
        return _ok(json.dumps({"id": container.short_id, "name": container.name}))
    except Exception as e:
        return _err(str(e))


def start_container(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        client = get_client()
        container = client.containers.get(container_id)
        container.start()
        return _ok(f"Container {container_id} started")
    except Exception as e:
        return _err(str(e))


def stop_container(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        client = get_client()
        container = client.containers.get(container_id)
        container.stop()
        return _ok(f"Container {container_id} stopped")
    except Exception as e:
        return _err(str(e))


def restart_container(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        client = get_client()
        container = client.containers.get(container_id)
        container.restart()
        return _ok(f"Container {container_id} restarted")
    except Exception as e:
        return _err(str(e))


def remove_container(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        force = args.get("force", False)
        client = get_client()
        container = client.containers.get(container_id)
        container.remove(force=force)
        return _ok(f"Container {container_id} removed")
    except Exception as e:
        return _err(str(e))


def container_logs(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        tail = args.get("tail", 100)
        client = get_client()
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail, stream=False)
        return _ok(logs.decode("utf-8", errors="replace"))
    except Exception as e:
        return _err(str(e))


def exec_container(args: dict) -> dict:
    try:
        container_id = args.get("id")
        if not container_id:
            return _err("'id' is required")

        command = args.get("command")
        if not isinstance(command, list):
            return _err("'command' must be a list of strings")

        client = get_client()
        container = client.containers.get(container_id)
        exit_code, output = container.exec_run(command)
        result = {
            "exit_code": exit_code,
            "output": output.decode("utf-8", errors="replace"),
        }
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))
