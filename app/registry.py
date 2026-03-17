from .tools.containers import (
    list_containers,
    create_container,
    start_container,
    stop_container,
    restart_container,
    remove_container,
    container_logs,
    exec_container,
)
from .tools.images import list_images, pull_image, build_image, remove_image
from .tools.networks import list_networks, create_network, remove_network
from .tools.volumes import list_volumes, create_volume, remove_volume
from .tools.compose import compose_up, compose_down, compose_logs
from .tools.system import docker_info_tool, docker_stats_tool, docker_prune_tool

TOOLS = [
    {
        "name": "docker_list_containers",
        "description": "List all Docker containers with their id, name, status, and image.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_create_container",
        "description": "Create a new Docker container.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image name to use"},
                "name": {"type": "string", "description": "Container name (optional)"},
                "command": {"type": "string", "description": "Command to run (optional)"},
                "environment": {
                    "type": "object",
                    "description": "Environment variables as key-value pairs (optional)",
                },
                "ports": {
                    "type": "object",
                    "description": "Port bindings as dict (optional)",
                },
            },
            "required": ["image"],
        },
    },
    {
        "name": "docker_start_container",
        "description": "Start a stopped Docker container by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "docker_stop_container",
        "description": "Stop a running Docker container by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "docker_restart_container",
        "description": "Restart a Docker container by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "docker_remove_container",
        "description": "Remove a Docker container by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
                "force": {"type": "boolean", "description": "Force removal even if running (default: false)"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "docker_logs",
        "description": "Retrieve logs from a Docker container.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
                "tail": {"type": "integer", "description": "Number of lines from end of logs (default: 100)"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "docker_exec",
        "description": "Execute a command inside a running Docker container. Command must be a list of strings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Container id or name"},
                "command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Command and arguments as a list of strings (e.g. ['ls', '-la'])",
                },
            },
            "required": ["id", "command"],
        },
    },
    {
        "name": "docker_list_images",
        "description": "List all Docker images with their id, tags, and size.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_pull_image",
        "description": "Pull a Docker image by name (e.g. alpine:latest).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Image name and tag (e.g. alpine:latest)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "docker_build_image",
        "description": "Build a Docker image from a Dockerfile at the given host path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the build context directory on the host"},
                "tag": {"type": "string", "description": "Tag for the built image (optional)"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "docker_remove_image",
        "description": "Remove a Docker image by name or id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Image name or id"},
                "force": {"type": "boolean", "description": "Force removal (default: false)"},
            },
            "required": [],
        },
    },
    {
        "name": "docker_list_networks",
        "description": "List all Docker networks with their id, name, and driver.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_create_network",
        "description": "Create a new Docker network.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Network name"},
                "driver": {"type": "string", "description": "Network driver (default: bridge)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "docker_remove_network",
        "description": "Remove a Docker network by id or name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Network id or name"},
            },
            "required": [],
        },
    },
    {
        "name": "docker_list_volumes",
        "description": "List all Docker volumes with their name, driver, and mountpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_create_volume",
        "description": "Create a new Docker volume.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Volume name"},
                "driver": {"type": "string", "description": "Volume driver (default: local)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "docker_remove_volume",
        "description": "Remove a Docker volume by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Volume name"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "docker_compose_up",
        "description": "Run 'docker compose up -d' in a whitelisted project path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Absolute path to the compose project directory"},
                "service": {"type": "string", "description": "Specific service to start (optional)"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "docker_compose_down",
        "description": "Run 'docker compose down' in a whitelisted project path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Absolute path to the compose project directory"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "docker_compose_logs",
        "description": "Retrieve logs from a Docker Compose project in a whitelisted path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Absolute path to the compose project directory"},
                "service": {"type": "string", "description": "Specific service to get logs for (optional)"},
                "tail": {"type": "integer", "description": "Number of lines from end (default: 50)"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "docker_info",
        "description": "Return Docker system information (version, resources, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_stats",
        "description": "Return a snapshot of CPU and memory stats for all running containers.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "docker_prune",
        "description": "Prune unused Docker resources. Target must be one of: containers, images, volumes, networks, all.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["containers", "images", "volumes", "networks", "all"],
                    "description": "Resource type to prune",
                },
            },
            "required": ["target"],
        },
    },
]

DISPATCHER = {
    "docker_list_containers": list_containers,
    "docker_create_container": create_container,
    "docker_start_container": start_container,
    "docker_stop_container": stop_container,
    "docker_restart_container": restart_container,
    "docker_remove_container": remove_container,
    "docker_logs": container_logs,
    "docker_exec": exec_container,
    "docker_list_images": list_images,
    "docker_pull_image": pull_image,
    "docker_build_image": build_image,
    "docker_remove_image": remove_image,
    "docker_list_networks": list_networks,
    "docker_create_network": create_network,
    "docker_remove_network": remove_network,
    "docker_list_volumes": list_volumes,
    "docker_create_volume": create_volume,
    "docker_remove_volume": remove_volume,
    "docker_compose_up": compose_up,
    "docker_compose_down": compose_down,
    "docker_compose_logs": compose_logs,
    "docker_info": docker_info_tool,
    "docker_stats": docker_stats_tool,
    "docker_prune": docker_prune_tool,
}
