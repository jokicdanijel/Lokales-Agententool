#!/usr/bin/env python3
"""
Agent Fleet Scanner (Docker-Compose Edition)
=============================================
Read-only scanner that discovers agent services from docker-compose files.
Extracts: service names, ports, image tags, health checks, and network topology.

Features:
- Live Docker status integration
- Historical change tracking
- Port conflict detection

Output: artifacts/agent_fleet/agent_inventory.json + agent_fleet_report.md
"""

import argparse
import json
import logging
import shutil
import sys
from collections import defaultdict
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


def get_docker_live_status(include_stats: bool = False) -> dict[str, dict[str, Any]]:
    """Get live status of Docker containers."""
    if not DOCKER_AVAILABLE:
        return {}

    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        status_map = {}
        for container in containers:
            container_info = {
                "status": container.status,
                "id": container.short_id,
                "created": container.attrs.get("Created", ""),
                "started_at": container.attrs.get("State", {}).get("StartedAt", ""),
                "health": container.attrs.get("State", {}).get("Health", {}).get("Status", "none"),
            }

            # Add resource stats if running and requested
            if include_stats and container.status == "running":
                try:
                    stats = container.stats(stream=False)

                    # CPU usage
                    cpu_delta = (
                        stats["cpu_stats"]["cpu_usage"]["total_usage"]
                        - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                    )
                    system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
                    cpu_percent = 0.0
                    if system_delta > 0 and cpu_delta > 0:
                        cpu_percent = (
                            (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0
                        )

                    # Memory usage
                    memory_usage = stats["memory_stats"].get("usage", 0)
                    memory_limit = stats["memory_stats"].get("limit", 1)
                    memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0

                    container_info["resources"] = {
                        "cpu_percent": round(cpu_percent, 2),
                        "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
                        "memory_limit_mb": round(memory_limit / (1024 * 1024), 2),
                        "memory_percent": round(memory_percent, 2),
                    }
                except Exception as e:
                    logger.debug(f"Could not get stats for {container.name}: {e}")

            status_map[container.name] = container_info

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


def load_previous_inventory(inventory_path: Path) -> dict[str, Any] | None:
    """Load previous inventory for change detection."""
    if not inventory_path.exists():
        return None

    try:
        with open(inventory_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load previous inventory: {e}")
        return None


def detect_changes(current: list[dict[str, Any]], previous: dict[str, Any] | None) -> dict[str, Any]:
    """Detect changes between current and previous inventory."""
    if not previous:
        return {
            "added": [s["service_name"] for s in current],
            "removed": [],
            "modified": [],
            "unchanged": [],
        }

    prev_services = {s["service_name"]: s for s in previous.get("services", [])}
    curr_services = {s["service_name"]: s for s in current}

    added = [name for name in curr_services if name not in prev_services]
    removed = [name for name in prev_services if name not in curr_services]

    modified = []
    unchanged = []

    for name in curr_services:
        if name in prev_services:
            # Compare key fields (ignoring live_status and scanned_at)
            curr = {k: v for k, v in curr_services[name].items() if k not in ["live_status", "scanned_at"]}
            prev = {k: v for k, v in prev_services[name].items() if k not in ["live_status", "scanned_at"]}

            if curr != prev:
                modified.append(name)
            else:
                unchanged.append(name)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def detect_port_conflicts(agents: list[dict[str, Any]]) -> dict[int, list[str]]:
    """Detect port conflicts (same host port used by multiple services)."""
    port_map = defaultdict(list)

    for agent in agents:
        for port in agent.get("ports", []):
            host_port = port.get("host_port")
            if isinstance(host_port, int):
                port_map[host_port].append(agent["service_name"])

    # Only return ports with conflicts
    conflicts = {port: services for port, services in port_map.items() if len(services) > 1}

    if conflicts:
        logger.warning(f"⚠️  Detected {len(conflicts)} port conflicts!")
        for port, services in conflicts.items():
            logger.warning(f"   Port {port}: {', '.join(services)}")

    return conflicts


def save_historical_snapshot(inventory_path: Path, history_dir: Path):
    """Save current inventory as historical snapshot."""
    if not inventory_path.exists():
        return

    history_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_path = history_dir / f"inventory_{timestamp}.json"

    shutil.copy(inventory_path, snapshot_path)
    logger.info(f"Historical snapshot saved: {snapshot_path.name}")

    # Keep only last 10 snapshots
    snapshots = sorted(history_dir.glob("inventory_*.json"))
    if len(snapshots) > 10:
        for old_snapshot in snapshots[:-10]:
            old_snapshot.unlink()
            logger.debug(f"Removed old snapshot: {old_snapshot.name}")


def scan_multiple_compose_files(
    compose_paths: list[Path], include_live_status: bool = True, include_resource_stats: bool = False
) -> list[dict[str, Any]]:
    """Scan multiple docker-compose files."""
    all_agents = []

    for compose_path in compose_paths:
        agents = scan_compose_file(compose_path)
        all_agents.extend(agents)

    # Enrich with live Docker status
    if include_live_status:
        live_status = get_docker_live_status(include_stats=include_resource_stats)
        all_agents = enrich_with_live_status(all_agents, live_status)

    return all_agents


def generate_markdown_report(
    agents: list[dict[str, Any]],
    output_path: Path,
    changes: dict[str, Any] | None = None,
    port_conflicts: dict[int, list[str]] | None = None,
):
    """Generate human-readable Markdown report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Agent Fleet Inventory Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
        f.write(f"**Total Services:** {len(agents)}\n\n")

        # Change summary
        if changes:
            f.write("## 📊 Change Summary\n\n")
            if changes["added"]:
                f.write(f"- ✅ **Added:** {len(changes['added'])} services\n")
                for service in changes["added"][:5]:
                    f.write(f"  - {service}\n")
                if len(changes["added"]) > 5:
                    f.write(f"  - ... and {len(changes['added']) - 5} more\n")
            if changes["removed"]:
                f.write(f"- ❌ **Removed:** {len(changes['removed'])} services\n")
                for service in changes["removed"][:5]:
                    f.write(f"  - {service}\n")
                if len(changes["removed"]) > 5:
                    f.write(f"  - ... and {len(changes['removed']) - 5} more\n")
            if changes["modified"]:
                f.write(f"- 🔄 **Modified:** {len(changes['modified'])} services\n")
                for service in changes["modified"][:5]:
                    f.write(f"  - {service}\n")
                if len(changes["modified"]) > 5:
                    f.write(f"  - ... and {len(changes['modified']) - 5} more\n")
            if not any([changes["added"], changes["removed"], changes["modified"]]):
                f.write("- ✨ **No changes detected**\n")
            f.write("\n")

        # Port conflicts
        if port_conflicts:
            f.write("## ⚠️  Port Conflicts\n\n")
            for port, services in sorted(port_conflicts.items()):
                f.write(f"- **Port {port}:** {', '.join(services)}\n")
            f.write("\n")

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

            # Resource stats if available
            if "live_status" in agent and "resources" in agent.get("live_status", {}):
                res = agent["live_status"]["resources"]
                f.write(
                    f"- **Resources:** CPU {res['cpu_percent']:.1f}% | RAM {res['memory_usage_mb']:.0f}MB ({res['memory_percent']:.1f}%)\n"
                )

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
    parser.add_argument(
        "--track-changes",
        action="store_true",
        default=True,
        help="Track changes from previous scan (default: True)",
    )
    parser.add_argument(
        "--no-track-changes",
        dest="track_changes",
        action="store_false",
        help="Disable change tracking",
    )
    parser.add_argument(
        "--detect-conflicts",
        action="store_true",
        default=True,
        help="Detect port conflicts (default: True)",
    )
    parser.add_argument(
        "--resource-stats",
        action="store_true",
        help="Include CPU/Memory stats (slower, only for running containers)",
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

    # Load previous inventory for change detection
    inventory_json = args.output_dir / "agent_inventory.json"
    previous_inventory = None
    if args.track_changes:
        # Save current inventory as historical snapshot before overwriting
        history_dir = args.output_dir / "history"
        save_historical_snapshot(inventory_json, history_dir)
        previous_inventory = load_previous_inventory(inventory_json)

    # Scan all compose files
    all_agents = scan_multiple_compose_files(
        compose_paths, include_live_status=args.live_status, include_resource_stats=args.resource_stats
    )

    # Detect changes
    changes = None
    if args.track_changes:
        changes = detect_changes(all_agents, previous_inventory)
        logger.info(f"Changes: +{len(changes['added'])} -{len(changes['removed'])} ~{len(changes['modified'])}")

    # Detect port conflicts
    port_conflicts = None
    if args.detect_conflicts:
        port_conflicts = detect_port_conflicts(all_agents)

    # Generate outputs
    report_md = args.output_dir / "agent_fleet_report.md"

    inventory_data = {
        "scanned_at": datetime.utcnow().isoformat() + "Z",
        "total_services": len(all_agents),
        "compose_files_scanned": [str(p) for p in compose_paths],
        "services": all_agents,
        "changes": changes,
        "port_conflicts": {str(k): v for k, v in port_conflicts.items()} if port_conflicts else {},
    }

    with open(inventory_json, "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Inventory JSON written to {inventory_json}")

    generate_markdown_report(all_agents, report_md, changes=changes, port_conflicts=port_conflicts)

    logger.info("✅ Agent fleet scan complete!")
    logger.info(f"   - Services discovered: {len(all_agents)}")
    logger.info(f"   - Compose files scanned: {len(compose_paths)}")
    logger.info(f"   - Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
