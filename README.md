# Docker MCP Gateway

## Overview

Docker MCP Gateway is an MCP (Model Context Protocol) server that exposes Docker operations to AI agents such as Claude Code. It runs as a containerized FastAPI application behind an Nginx reverse proxy, accepting authenticated SSE connections and translating MCP tool calls into Docker API operations.

This lets you give an AI agent controlled, auditable access to Docker on a remote host — start/stop containers, read logs, manage images, networks, volumes, and run `docker compose` operations — all over a single HTTPS endpoint secured with a Bearer token.

---

## Security Warning

**Mounting `/var/run/docker.sock` gives the gateway process effective root access on the host.** Any authenticated client can create privileged containers, mount host paths, or escape the container entirely.

Recommended threat model for safe operation:

- Run on an **isolated VPS** dedicated to this gateway. Do not share the host with other workloads.
- **Enable the IP whitelist** in `nginx/nginx.conf` so only your known egress IPs can reach the endpoint.
- Use a **strong Bearer token** (minimum 32 random bytes). The gateway enforces this at startup.
- **Never expose this on shared or multi-tenant infrastructure.**

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/docker-mcp-gateway.git
cd docker-mcp-gateway

# 2. Create your environment file
cp .env.example .env
# Edit .env: set MCP_AUTH_TOKEN to the output of: openssl rand -hex 32

# 3. Start the gateway
docker compose up -d --build

# 4. Verify the gateway is healthy
curl http://localhost:3000/health
```

Expected response: `{"status": "ok"}`

---

## VPS Setup

Complete setup for a production deployment with TLS.

### 1. Install Docker and docker compose

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker compose version
```

### 2. Point your domain to the VPS

Create an A record:

```
mcp.yourdomain.com  →  <your-vps-ip>
```

Wait for DNS propagation before proceeding.

### 3. Install Certbot and obtain a certificate

```bash
sudo apt-get update
sudo apt-get install -y certbot

# Stop anything using port 80, then:
sudo certbot certonly --standalone -d mcp.yourdomain.com
```

Certificates are written to `/etc/letsencrypt/live/mcp.yourdomain.com/`. The `docker-compose.yml` mounts `/etc/letsencrypt` into the Nginx container read-only.

### 4. Set up automatic renewal

```bash
# Dry run to confirm renewal works
sudo certbot renew --dry-run

# The certbot package installs a systemd timer or cron job automatically.
# Verify it is active:
sudo systemctl status certbot.timer
```

### 5. Update nginx.conf for your domain

Edit `nginx/nginx.conf` and replace `mcp.yourdomain.com` with your actual domain in the `server_name` and `ssl_certificate` directives.

### 6. Generate and set the token

```bash
openssl rand -hex 32
# Copy the output into .env as MCP_AUTH_TOKEN
```

### 7. Start the stack

```bash
docker compose up -d --build
curl https://mcp.yourdomain.com/health
```

---

## Claude Code Configuration

### Global configuration

Applies to all projects. Edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "docker-gateway": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
      }
    }
  }
}
```

### Per-project configuration

Applies only to a specific project. Edit `.claude/settings.json` in the project root:

```json
{
  "mcpServers": {
    "docker-gateway": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
      }
    }
  }
}
```

Replace `YOUR_MCP_AUTH_TOKEN` with the value from your `.env` file.

---

## Available Tools

### Containers

| Tool | Description |
|------|-------------|
| `container_list` | List all containers (running and stopped) |
| `container_create` | Create a new container from an image |
| `container_start` | Start a stopped container |
| `container_stop` | Stop a running container |
| `container_restart` | Restart a container |
| `container_remove` | Remove a container (supports force flag) |
| `container_logs` | Fetch container logs (tail N lines) |
| `container_exec` | Execute a command inside a running container |

### Images

| Tool | Description |
|------|-------------|
| `image_list` | List locally available images |
| `image_pull` | Pull an image from a registry |
| `image_remove` | Remove a local image |
| `image_inspect` | Return detailed image metadata |

### Networks

| Tool | Description |
|------|-------------|
| `network_list` | List Docker networks |
| `network_create` | Create a new network |
| `network_remove` | Remove a network |

### Volumes

| Tool | Description |
|------|-------------|
| `volume_list` | List Docker volumes |
| `volume_create` | Create a named volume |
| `volume_remove` | Remove a volume |

### Compose

| Tool | Description |
|------|-------------|
| `compose_up` | Run `docker compose up -d` for a project path |
| `compose_down` | Run `docker compose down` for a project path |
| `compose_ps` | List services and their status for a project |

### System

| Tool | Description |
|------|-------------|
| `system_info` | Return Docker host info (version, OS, resources) |
| `system_prune` | Remove unused containers, networks, and images |

---

## Security Hardening

### IP whitelist

Uncomment and populate the whitelist block in `nginx/nginx.conf`:

```nginx
# IP Whitelist -- replace with your IPs
allow 1.2.3.4;
allow 5.6.7.8;
deny all;
```

Restart Nginx after changes: `docker compose restart nginx`

### Bearer token length

`auth.py` enforces a minimum token length of 32 characters at request time. If `MCP_AUTH_TOKEN` is absent or shorter than 32 characters, the gateway returns HTTP 500 and refuses all requests. Generate a compliant token with:

```bash
openssl rand -hex 32
```

### Compose path whitelist

Set `COMPOSE_PROJECT_PATH_WHITELIST` in `.env` to restrict which host directories the `compose_*` tools may operate on:

```
COMPOSE_PROJECT_PATH_WHITELIST=/opt/myapp:/opt/otherapp
```

Any compose tool call referencing a path outside this list is rejected before it reaches the Docker daemon.

### docker.sock isolation

The Docker socket grants unrestricted access to the Docker daemon and, through it, to the host. Mitigations:

- Run the gateway on a dedicated VPS with no other sensitive workloads.
- Keep the OS and Docker engine updated.
- Do not expose port 3000 directly; let all traffic flow through Nginx on 443.
- Consider using a Docker socket proxy (e.g., Tecnativa/docker-socket-proxy) to restrict which Docker API endpoints are accessible, if you need further confinement.

### Rate limiting

Nginx applies a zone-based rate limit of **30 requests per minute per IP** with a burst allowance of 10. This is configured in `nginx/nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=30r/m;
limit_req zone=mcp_limit burst=10 nodelay;
```

Adjust `rate` and `burst` to match your expected agent call volume.

---

## Troubleshooting

### Gateway cannot connect to Docker

```
RuntimeError: Cannot connect to Docker socket
```

Verify the socket is mounted and the gateway user has access:

```bash
# Check the mount
docker inspect docker-mcp-gateway-gateway-1 | grep -A5 Mounts

# Check socket permissions on the host
ls -la /var/run/docker.sock

# Add the container user to the docker group if needed, or chmod the socket (not recommended for production)
```

### 401 Unauthorized

The Bearer token in the client request does not match `MCP_AUTH_TOKEN` in `.env`.

1. Confirm the value in `.env`: `grep MCP_AUTH_TOKEN .env`
2. Confirm the value in your Claude config matches exactly (no trailing whitespace).
3. Restart the gateway after any `.env` change: `docker compose restart gateway`

### SSE connection drops

Increase the Nginx keepalive timeout in `nginx/nginx.conf`:

```nginx
keepalive_timeout 3600s;
proxy_read_timeout 3600s;
```

The default configuration already sets both to 3600s. If connections still drop, check for an upstream load balancer or firewall with a shorter idle timeout.

### 403 Forbidden from Nginx

Your client IP is not in the whitelist. Either add the IP to the `allow` list in `nginx/nginx.conf`, or comment out the whitelist block if you want to allow all IPs (not recommended for production).
