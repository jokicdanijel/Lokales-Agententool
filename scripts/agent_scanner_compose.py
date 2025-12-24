#!/usr/bin/env python3
"""
Agent Fleet Scanner (Docker-Compose Edition)
=============================================
Read-only scanner that discovers agent services from docker-compose files.
Extracts: service names, ports, image tags, health checks, and network topology.

Output: artifacts/agent_fleet/agent_inventory.json + agent_fleet_report.md
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("Docker SDK not installed. Live status will be unavailable. Install: pip install docker")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_compose_file(compose_path: Path) -> dict[str, Any]:
    """Parse docker-compose.yml and extract service definitions."""
    try:
        with open(compose_path, encoding="utf-8") as f:
            compose_data = yaml.safe_load(f)

        if not compose_data or "services" not in compose_data:
            logger.warning(f"No services found in {compose_path}")
            return {}

        return compose_data
    except FileNotFoundError:
        logger.error(f"Compose file not found: {compose_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error in {compose_path}: {e}")
        return {}


def extract_ports(service_config: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract port mappings from service configuration."""
    ports = []
    port_specs = service_config.get("ports", [])

    for port_spec in port_specs:
        if isinstance(port_spec, str):
            parts = port_spec.split(":")
            if len(parts) >= 2:
                host_port = parts[0]
                container_port = parts[-1].split("/")[0]
                protocol = "tcp"
                if "/" in parts[-1]:
                    protocol = parts[-1].split("/")[1]

                ports.append(
                    {
                        "host_port": int(host_port) if host_port.isdigit() else host_port,
                        "container_port": int(container_port) if container_port.isdigit() else container_port,
                        "protocol": protocol,
                    }
                )
        elif isinstance(port_spec, dict):
            ports.append(
                {
                    "host_port": port_spec.get("published", "unknown"),
                    "container_port": port_spec.get("target", "unknown"),
                    "protocol": port_spec.get("protocol", "tcp"),
                }
            )

    return ports


def extract_environment(service_config: dict[str, Any]) -> dict[str, str]:
    """Extract environment variables (sanitized - no secrets)."""
    env = {}
    env_specs = service_config.get("environment", [])

    if isinstance(env_specs, list):
        for item in env_specs:
            if "=" in item:
                key, value = item.split("=", 1)
                # Sanitize secrets
                if any(secret_word in key.upper() for secret_word in ["PASSWORD", "SECRET", "TOKEN", "KEY", "API"]):
                    value = "***REDACTED***"
                env[key] = value
    elif isinstance(env_specs, dict):
        for key, value in env_specs.items():
            if any(secret_word in key.upper() for secret_word in ["PASSWORD", "SECRET", "TOKEN", "KEY", "API"]):
                value = "***REDACTED***"
            env[key] = str(value) if value is not None else ""

    return env


def extract_health_check(service_config: dict[str, Any]) -> dict[str, Any] | None:
    """Extract health check configuration."""
    healthcheck = service_config.get("healthcheck")
    if not healthcheck:
        return None

    return {
        "test": healthcheck.get("test", []),
        "interval": healthcheck.get("interval", "unknown"),
        "timeout": healthcheck.get("timeout", "unknown"),
        "retries": healthcheck.get("retries", 3),
    }


def get_docker_live_status() -> dict[str, dict[str, Any]]:
    """Get live status of Docker containers."""
    if not DOCKER_AVAILABLE:
        return {}

    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        status_map = {}
        for container in containers:
            status_map[container.name] = {
                "status": container.status,
                "id": container.short_id,
                "created": container.attrs.get("Created", ""),
                "started_at": container.attrs.get("State", {}).get("StartedAt", ""),
                "health": container.attrs.get("State", {}).get("Health", {}).get("Status", "none"),
            }

        logger.info(f"Retrieved live status for {len(status_map)} containers")
        return status_map
    except Exception as e:
        logger.warning(f"Could not connect to Docker daemon: {e}")
        return {}


def enrich_with_live_status(
    agents: list[dict[str, Any]], live_status: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Enrich agent data with live Docker status."""
    for agent in agents:
        container_name = agent.get("container_name", "")
        if container_name in live_status:
            agent["live_status"] = live_status[container_name]
        else:
            agent["live_status"] = {
                "status": "not_found",
                "id": None,
                "created": None,
                "started_at": None,
                "health": "none",
            }

    return agents


def scan_compose_file(compose_path: Path, project_name: str | None = None) -> list[dict[str, Any]]:
    """Scan a docker-compose file and extract all agent services."""
    logger.info(f"Scanning compose file: {compose_path}")
    compose_data = parse_compose_file(compose_path)

    if not compose_data:
        return []

    services = compose_data.get("services", {})
    agents = []

    for service_name, service_config in services.items():
        agent_info = {
            "service_name": service_name,
            "compose_file": str(compose_path),
            "project_name": project_name or compose_path.parent.name,
            "image": service_config.get("image", "unknown"),
            "container_name": service_config.get("container_name", service_name),
            "ports": extract_ports(service_config),
            "environment": extract_environment(service_config),
            "volumes": service_config.get("volumes", []),
            "networks": (
                list(service_config.get("networks", {}).keys())
                if isinstance(service_config.get("networks"), dict)
                else service_config.get("networks", [])
            ),
            "depends_on": service_config.get("depends_on", []),
            "restart": service_config.get("restart", "no"),
            "healthcheck": extract_health_check(service_config),
            "command": service_config.get("command", None),
            "working_dir": service_config.get("working_dir", None),
            "scanned_at": datetime.utcnow().isoformat() + "Z",
        }

        agents.append(agent_info)

    logger.info(f"Found {len(agents)} services in {compose_path.name}")
    return agents


def scan_multiple_compose_files(compose_paths: list[Path], include_live_status: bool = True) -> list[dict[str, Any]]:
    """Scan multiple docker-compose files."""
    all_agents = []

    for compose_path in compose_paths:
        agents = scan_compose_file(compose_path)
        all_agents.extend(agents)

    # Enrich with live Docker status
    if include_live_status:
        live_status = get_docker_live_status()
        all_agents = enrich_with_live_status(all_agents, live_status)

    return all_agents


def generate_markdown_report(agents: list[dict[str, Any]], output_path: Path):
    """Generate human-readable Markdown report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Agent Fleet Inventory Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write(f"**Total Services:** {len(agents)}\n\n")
        f.write("---\n\n")

        for agent in agents:
            f.write(f"## {agent['service_name']}\n\n")

            # Live status badge
            if "live_status" in agent:
                live = agent["live_status"]
                status_emoji = (
                    "🟢" if live["status"] == "running" else "🔴" if live["status"] in ["exited", "stopped"] else "⚪"
                )
                f.write(f"**Status:** {status_emoji} {live['status'].upper()}")
                if live["id"]:
                    f.write(f" (ID: `{live['id']}`)")
                f.write("\n\n")

            f.write(f"- **Image:** `{agent['image']}`\n")
            f.write(f"- **Container:** `{agent['container_name']}`\n")
            f.write(f"- **Compose File:** `{agent['compose_file']}`\n")
            f.write(f"- **Restart Policy:** `{agent['restart']}`\n")

            if agent["ports"]:
                f.write("- **Ports:**\n")
                for port in agent["ports"]:
                    f.write(f"  - `{port['host_port']}` → `{port['container_port']}` ({port['protocol']})\n")

            if agent["networks"]:
                f.write(f"- **Networks:** {', '.join(agent['networks'])}\n")

            if agent["depends_on"]:
                f.write(f"- **Dependencies:** {', '.join(agent['depends_on'])}\n")

            if agent["healthcheck"]:
                f.write(f"- **Health Check:** {agent['healthcheck']['test']}\n")

            f.write("\n---\n\n")

    logger.info(f"Markdown report written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Agent Fleet Scanner for Docker-Compose")
    parser.add_argument(
        "--compose-files",
        nargs="+",
        default=["./docker-compose.yml"],
        help="Paths to docker-compose files (default: ./docker-compose.yml)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("19.opena20_dashboard_agent/artifacts/agent_fleet"),
        help="Output directory for inventory files",
    )
    parser.add_argument(
        "--auto-discover",
        action="store_true",
        help="Auto-discover all docker-compose.yml files in repository",
    )
    parser.add_argument(
        "--live-status",
        action="store_true",
        default=True,
        help="Include live Docker container status (default: True)",
    )
    parser.add_argument(
        "--no-live-status",
        dest="live_status",
        action="store_false",
        help="Disable live Docker status integration",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which compose files to scan
    compose_paths = []
    if args.auto_discover:
        logger.info("Auto-discovering docker-compose files...")
        repo_root = Path.cwd()
        compose_paths = list(repo_root.rglob("docker-compose*.yml"))
        compose_paths.extend(list(repo_root.rglob("docker-compose*.yaml")))
        # Exclude node_modules and hidden directories
        compose_paths = [
            p
            for p in compose_paths
            if "node_modules" not in str(p) and not any(part.startswith(".") for part in p.parts)
        ]
        logger.info(f"Discovered {len(compose_paths)} compose files")
    else:
        compose_paths = [Path(p) for p in args.compose_files]

    # Scan all compose files
    all_agents = scan_multiple_compose_files(compose_paths, include_live_status=args.live_status)

    # Generate outputs
    inventory_json = args.output_dir / "agent_inventory.json"
    report_md = args.output_dir / "agent_fleet_report.md"

    inventory_data = {
        "scanned_at": datetime.utcnow().isoformat() + "Z",
        "total_services": len(all_agents),
        "compose_files_scanned": [str(p) for p in compose_paths],
        "services": all_agents,
    }

    with open(inventory_json, "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Inventory JSON written to {inventory_json}")

    generate_markdown_report(all_agents, report_md)

    logger.info("✅ Agent fleet scan complete!")
    logger.info(f"   - Services discovered: {len(all_agents)}")
    logger.info(f"   - Compose files scanned: {len(compose_paths)}")
    logger.info(f"   - Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
