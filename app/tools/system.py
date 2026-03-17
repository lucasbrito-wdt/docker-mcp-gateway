import json
from docker_client import get_client


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def docker_info_tool(args: dict) -> dict:
    try:
        client = get_client()
        info = client.info()
        return _ok(json.dumps(info))
    except Exception as e:
        return _err(str(e))


def docker_stats_tool(args: dict) -> dict:
    try:
        client = get_client()
        containers = client.containers.list()
        result = []

        for container in containers:
            stats = container.stats(stream=False)
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"].get("system_cpu_usage", 0)
                - stats["precpu_stats"].get("system_cpu_usage", 0)
            )
            num_cpus = stats["cpu_stats"].get("online_cpus") or len(
                stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1])
            )
            cpu_percent = (cpu_delta / system_delta * num_cpus * 100.0) if system_delta > 0 else 0.0

            mem_usage = stats["memory_stats"].get("usage", 0)

            result.append(
                {
                    "id": container.short_id,
                    "name": container.name,
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_usage": mem_usage,
                }
            )

        return _ok(json.dumps(result))
    except Exception as e:
        return _err(str(e))


def docker_prune_tool(args: dict) -> dict:
    try:
        target = args.get("target")
        valid_targets = {"containers", "images", "volumes", "networks", "all"}

        if target not in valid_targets:
            return _err(f"'target' must be one of: {', '.join(sorted(valid_targets))}")

        client = get_client()
        results = {}

        if target in ("containers", "all"):
            results["containers"] = client.containers.prune()

        if target in ("images", "all"):
            results["images"] = client.images.prune()

        if target in ("volumes", "all"):
            results["volumes"] = client.volumes.prune()

        if target in ("networks", "all"):
            results["networks"] = client.networks.prune()

        return _ok(json.dumps(results))
    except Exception as e:
        return _err(str(e))
