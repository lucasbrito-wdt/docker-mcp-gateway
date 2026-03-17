import os
import subprocess


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"error": text}


def _is_path_allowed(path: str) -> bool:
    whitelist_raw = os.environ.get("COMPOSE_PROJECT_PATH_WHITELIST", "")
    if not whitelist_raw:
        return False

    allowed_paths = [p.strip() for p in whitelist_raw.split(":") if p.strip()]
    normalized = os.path.realpath(path)

    return any(normalized == os.path.realpath(p) for p in allowed_paths)


def _run(cmd: list, cwd: str) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    return output.strip()


def compose_up(args: dict) -> dict:
    try:
        project_path = args.get("project_path")
        if not project_path:
            return _err("'project_path' is required")

        if not _is_path_allowed(project_path):
            return _err("path not in whitelist")

        cmd = ["docker", "compose", "up", "-d"]
        service = args.get("service")
        if service:
            cmd.append(service)

        output = _run(cmd, cwd=project_path)
        return _ok(output)
    except Exception as e:
        return _err(str(e))


def compose_down(args: dict) -> dict:
    try:
        project_path = args.get("project_path")
        if not project_path:
            return _err("'project_path' is required")

        if not _is_path_allowed(project_path):
            return _err("path not in whitelist")

        output = _run(["docker", "compose", "down"], cwd=project_path)
        return _ok(output)
    except Exception as e:
        return _err(str(e))


def compose_logs(args: dict) -> dict:
    try:
        project_path = args.get("project_path")
        if not project_path:
            return _err("'project_path' is required")

        if not _is_path_allowed(project_path):
            return _err("path not in whitelist")

        tail = args.get("tail", 50)
        cmd = ["docker", "compose", "logs", f"--tail={tail}"]
        service = args.get("service")
        if service:
            cmd.append(service)

        output = _run(cmd, cwd=project_path)
        return _ok(output)
    except Exception as e:
        return _err(str(e))
