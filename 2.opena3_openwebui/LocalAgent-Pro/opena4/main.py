#!/usr/bin/env python3
"""
opena4 - Compute Service
High-performance HTTP service for computation tasks with authentication,
monitoring, and comprehensive error handling.
"""

import http.server
import socketserver
import json
import time
import logging
import os
import sys
from typing import Dict, Optional, Tuple
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global metrics
_metrics = {
    "requests": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat(),
    "last_request": None,
    "response_times": []
}
_metrics_lock = threading.Lock()


class ConfigManager:
    """Load and manage configuration from file and environment variables."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from config.json and environment variables."""
        try:
            # Load from config.json
            config_file = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"✅ Config loaded from {config_file}")
            else:
                logger.warning(f"Config file not found: {config_file}")
                config = {"service": "opena4", "port": 12348}

            # Override with environment variables
            config['port'] = int(os.getenv('OPENA4_PORT', config.get('port', 12348)))
            config['bearer_token'] = os.getenv(
                'OPENA4_BEARER_TOKEN',
                os.getenv('BEARER_TOKEN', 'sk_opena4_compute_v3_production')
            )
            config['log_level'] = os.getenv('OPENA4_LOG_LEVEL', config.get('log_level', 'INFO'))
            config['max_workers'] = int(os.getenv('OPENA4_MAX_WORKERS', config.get('max_workers', 4)))
            config['timeout'] = int(os.getenv('OPENA4_TIMEOUT', config.get('timeout', 30)))

            # Update logging level
            logging.getLogger().setLevel(config['log_level'])

            return config

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self._config.get(key, default)

    def __getitem__(self, key: str):
        """Support dictionary-like access."""
        return self._config[key]


def validate_bearer_token(auth_header: Optional[str], expected_token: str) -> bool:
    """
    Validate Bearer token from Authorization header.

    Args:
        auth_header: Authorization header value
        expected_token: Expected token value

    Returns:
        True if token is valid, False otherwise
    """
    if not auth_header:
        return False

    try:
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return False

        token = parts[1]
        return token == expected_token

    except Exception as e:
        logger.warning(f"Error validating bearer token: {e}")
        return False


class ComputeHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for compute service."""

    def _send_json_response(
        self,
        status_code: int,
        data: Dict,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Send JSON response with standard headers.

        Args:
            status_code: HTTP status code
            data: Response data dictionary
            headers: Optional additional headers
        """
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("X-Service", "opena4")

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)

        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _update_metrics(self, response_time: float) -> None:
        """Update metrics after request processing."""
        with _metrics_lock:
            _metrics["requests"] += 1
            _metrics["last_request"] = datetime.now().isoformat()
            _metrics["response_times"].append(response_time)
            # Keep only last 100 response times
            if len(_metrics["response_times"]) > 100:
                _metrics["response_times"].pop(0)

    def do_GET(self) -> None:
        """Handle GET requests."""
        start_time = time.time()
        config = ConfigManager()

        try:
            if self.path == "/health":
                self._handle_health()
            elif self.path == "/metrics":
                self._handle_metrics()
            else:
                self._send_json_response(
                    404,
                    {"error": "Endpoint not found", "path": self.path}
                )

        except Exception as e:
            logger.error(f"Error handling GET {self.path}: {e}")
            with _metrics_lock:
                _metrics["errors"] += 1
            self._send_json_response(
                500,
                {"error": "Internal server error", "details": str(e)}
            )

        finally:
            response_time = time.time() - start_time
            self._update_metrics(response_time)
            logger.debug(f"GET {self.path} - {response_time:.3f}s")

    def do_POST(self) -> None:
        """Handle POST requests with authentication."""
        start_time = time.time()
        config = ConfigManager()

        try:
            # Validate authentication
            auth_header = self.headers.get("Authorization")
            if not validate_bearer_token(auth_header, config["bearer_token"]):
                logger.warning(f"Unauthorized POST attempt to {self.path}")
                self._send_json_response(401, {"error": "Unauthorized"})
                return

            if self.path == "/compute":
                self._handle_compute()
            else:
                self._send_json_response(
                    404,
                    {"error": "Endpoint not found", "path": self.path}
                )

        except Exception as e:
            logger.error(f"Error handling POST {self.path}: {e}")
            with _metrics_lock:
                _metrics["errors"] += 1
            self._send_json_response(
                500,
                {"error": "Internal server error", "details": str(e)}
            )

        finally:
            response_time = time.time() - start_time
            self._update_metrics(response_time)
            logger.debug(f"POST {self.path} - {response_time:.3f}s")

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _handle_health(self) -> None:
        """Handle /health endpoint."""
        config = ConfigManager()
        self._send_json_response(
            200,
            {
                "status": "online",
                "service": config.get("service", "opena4"),
                "port": config.get("port"),
                "version": config.get("version", "3.0.0"),
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.fromisoformat(_metrics["start_time"]) - datetime.now()).total_seconds()
            }
        )

    def _handle_metrics(self) -> None:
        """Handle /metrics endpoint."""
        with _metrics_lock:
            avg_response_time = (
                sum(_metrics["response_times"]) / len(_metrics["response_times"])
                if _metrics["response_times"] else 0
            )

            self._send_json_response(
                200,
                {
                    "requests": _metrics["requests"],
                    "errors": _metrics["errors"],
                    "start_time": _metrics["start_time"],
                    "last_request": _metrics["last_request"],
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "error_rate": (
                        _metrics["errors"] / _metrics["requests"] * 100
                        if _metrics["requests"] > 0 else 0
                    )
                }
            )

    def _handle_compute(self) -> None:
        """Handle /compute endpoint (placeholder)."""
        config = ConfigManager()
        content_length = int(self.headers.get('Content-Length', 0))

        if content_length == 0:
            self._send_json_response(
                400,
                {"error": "No request body provided"}
            )
            return

        try:
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode())

            # Placeholder computation
            result = {
                "status": "completed",
                "input": request_data,
                "computation": "placeholder",
                "timestamp": datetime.now().isoformat()
            }

            self._send_json_response(200, result)

        except json.JSONDecodeError:
            self._send_json_response(
                400,
                {"error": "Invalid JSON in request body"}
            )

    def log_message(self, format: str, *args) -> None:
        """Override to use structured logging instead."""
        logger.debug(format % args)


def main() -> None:
    """Start the compute service server."""
    config = ConfigManager()
    host = "0.0.0.0"
    port = config["port"]
    service_name = config.get("service", "opena4")

    logger.info(f"═" * 70)
    logger.info(f"🚀 {service_name.upper()} Compute Service Starting")
    logger.info(f"═" * 70)
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Service: {service_name}")
    logger.info(f"  Max Workers: {config.get('max_workers')}")
    logger.info(f"  Timeout: {config.get('timeout')}s")
    logger.info(f"  Log Level: {config.get('log_level')}")
    logger.info(f"═" * 70)

    try:
        with socketserver.TCPServer((host, port), ComputeHandler) as httpd:
            logger.info(f"✅ Server running on http://{host}:{port}")
            logger.info(f"  Health: http://{host}:{port}/health")
            logger.info(f"  Metrics: http://{host}:{port}/metrics")

            httpd.serve_forever()

    except OSError as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutting down gracefully...")

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        logger.info("✅ Server stopped")


if __name__ == "__main__":
    main()
