import json
from ..docker_client import get_client


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def list_images(args: dict) -> dict:
    try:
        client = get_client()
        images = client.images.list()
        result = [
            {
                "id": img.short_id,
                "tags": img.tags,
                "size": img.attrs.get("Size", 0),
            }
            for img in images
        ]
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def pull_image(args: dict) -> dict:
    try:
        name = args.get("name")
        if not name:
            return _err("'name' is required")

        client = get_client()
        progress_lines = []
        for line in client.api.pull(name, stream=True, decode=True):
            status = line.get("status", "")
            progress = line.get("progress", "")
            if status:
                progress_lines.append(f"{status} {progress}".strip())

        return _ok("\n".join(progress_lines) or f"Pulled {name}")
    except Exception as e:
        return _err(str(e))


def build_image(args: dict) -> dict:
    try:
        path = args.get("path")
        if not path:
            return _err("'path' is required")

        tag = args.get("tag")
        client = get_client()
        image, logs = client.images.build(path=path, tag=tag)
        log_lines = [
            line.get("stream", "").strip()
            for line in logs
            if line.get("stream", "").strip()
        ]
        result = {
            "id": image.short_id,
            "tags": image.tags,
            "logs": log_lines,
        }
        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def remove_image(args: dict) -> dict:
    try:
        name = args.get("name") or args.get("id")
        if not name:
            return _err("'name' or 'id' is required")

        force = args.get("force", False)
        client = get_client()
        client.images.remove(name, force=force)
        return _ok(f"Image {name} removed")
    except Exception as e:
        return _err(str(e))
