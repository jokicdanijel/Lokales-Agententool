#!/usr/bin/env python3
"""
LocalAgent-Pro - OpenWebUI Agent Server
Production-ready AI-Agent-Server with OpenWebUI integration
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'config.yaml'
with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Constants
SANDBOX_DIR = Path.home() / 'localagent_sandbox'
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', CONFIG['ollama']['base_url'])
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', CONFIG['ollama']['model'])
ALLOWED_COMMANDS = CONFIG['security']['shell_whitelist']
DANGEROUS_COMMANDS = CONFIG['security']['dangerous_commands']

# Request deduplication cache
request_cache = set()
MAX_CACHE_SIZE = 1000

# Create sandbox directory
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"Sandbox directory: {SANDBOX_DIR}")


class SecurityError(Exception):
    """Raised when a security violation is detected"""
    pass


def sanitize_filename(filename: str) -> Path:
    """Sanitize filename and return safe path within sandbox"""
    if '..' in filename or filename.startswith('/'):
        raise SecurityError(f"Path traversal detected: {filename}")
    
    safe_path = SANDBOX_DIR / filename
    
    # Ensure path is within sandbox
    if not str(safe_path.resolve()).startswith(str(SANDBOX_DIR.resolve())):
        raise SecurityError(f"Path outside sandbox: {filename}")
    
    return safe_path


def check_command_safety(command: str) -> bool:
    """Check if command is safe to execute"""
    # Check for dangerous commands
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command:
            raise SecurityError(f"Dangerous command detected: {dangerous}")
    
    # Extract base command
    base_cmd = command.split()[0] if command else ""
    
    # Check whitelist
    if base_cmd not in ALLOWED_COMMANDS:
        raise SecurityError(f"Command not whitelisted: {base_cmd}")
    
    return True


def check_duplicate_request(request_data: dict) -> bool:
    """Check for duplicate requests using MD5 hash"""
    request_str = json.dumps(request_data, sort_keys=True)
    request_hash = hashlib.md5(request_str.encode()).hexdigest()
    
    if request_hash in request_cache:
        logger.warning(f"Duplicate request detected: {request_hash}")
        return True
    
    # Add to cache
    request_cache.add(request_hash)
    
    # Limit cache size
    if len(request_cache) > MAX_CACHE_SIZE:
        request_cache.pop()
    
    return False


def write_file(filename: str, content: str) -> dict:
    """Write content to file in sandbox"""
    try:
        file_path = sanitize_filename(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"File created: {filename}")
        return {
            "status": "success",
            "message": f"File created: {filename}",
            "path": str(file_path)
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return {"status": "error", "message": str(e)}


def read_file(filename: str) -> dict:
    """Read file from sandbox"""
    try:
        file_path = sanitize_filename(filename)
        
        if not file_path.exists():
            return {"status": "error", "message": f"File not found: {filename}"}
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"File read: {filename}")
        return {
            "status": "success",
            "content": content,
            "path": str(file_path)
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {"status": "error", "message": str(e)}


def delete_file(filename: str) -> dict:
    """Delete file from sandbox"""
    try:
        file_path = sanitize_filename(filename)
        
        if not file_path.exists():
            return {"status": "error", "message": f"File not found: {filename}"}
        
        file_path.unlink()
        
        logger.info(f"File deleted: {filename}")
        return {
            "status": "success",
            "message": f"File deleted: {filename}"
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return {"status": "error", "message": str(e)}


def shell_exec(command: str) -> dict:
    """Execute shell command (whitelisted only)"""
    try:
        check_command_safety(command)
        
        import subprocess
        result = subprocess.run(
            command,
            shell=True,
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        logger.info(f"Command executed: {command}")
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {"status": "error", "message": str(e)}


def fetch_webpage(url: str) -> dict:
    """Fetch webpage content (whitelisted domains only)"""
    try:
        # Check domain whitelist
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        allowed_domains = CONFIG['security']['domain_whitelist']
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise SecurityError(f"Domain not whitelisted: {domain}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Webpage fetched: {url}")
        return {
            "status": "success",
            "content": response.text[:5000],  # Limit response size
            "status_code": response.status_code
        }
    except SecurityError as e:
        logger.error(f"Security error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error fetching webpage: {e}")
        return {"status": "error", "message": str(e)}


def process_tool_call(messages: List[dict]) -> Optional[dict]:
    """Process tool calls from chat messages"""
    if not messages:
        return None
    
    last_message = messages[-1]['content'].lower()
    
    # Detect file operations
    if 'erstelle' in last_message or 'write' in last_message:
        # Extract filename and content
        parts = messages[-1]['content'].split('\n', 1)
        if len(parts) == 2:
            filename = parts[0].split()[-1]
            content = parts[1]
            return write_file(filename, content)
    
    elif 'lies' in last_message or 'read' in last_message:
        # Extract filename
        words = messages[-1]['content'].split()
        for word in words:
            if '.' in word:
                return read_file(word)
    
    elif 'lösche' in last_message or 'delete' in last_message:
        # Extract filename
        words = messages[-1]['content'].split()
        for word in words:
            if '.' in word:
                return delete_file(word)
    
    elif 'führe aus' in last_message or 'execute' in last_message or 'command' in last_message:
        # Extract command
        if ':' in messages[-1]['content']:
            command = messages[-1]['content'].split(':', 1)[1].strip()
            return shell_exec(command)
    
    elif 'hole' in last_message or 'fetch' in last_message:
        # Extract URL
        words = messages[-1]['content'].split()
        for word in words:
            if word.startswith('http'):
                return fetch_webpage(word)
    
    return None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "sandbox": str(SANDBOX_DIR),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        models = response.json()
        
        return jsonify({
            "object": "list",
            "data": [
                {
                    "id": OLLAMA_MODEL,
                    "object": "model",
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "localagent-pro"
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Chat completions endpoint"""
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Check for duplicate requests
        if check_duplicate_request(data):
            return jsonify({"error": "Duplicate request"}), 429
        
        # Process tool calls
        tool_result = process_tool_call(messages)
        
        if tool_result:
            # Return tool result
            response_content = f"Tool executed: {json.dumps(tool_result, indent=2)}"
        else:
            # Forward to Ollama
            ollama_response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )
            
            ollama_data = ollama_response.json()
            response_content = ollama_data.get('message', {}).get('content', '')
        
        return jsonify({
            "id": f"chatcmpl-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": OLLAMA_MODEL,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ]
        })
    
    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total {{method="POST",endpoint="/v1/chat/completions"}} {len(request_cache)}

# HELP sandbox_files Total files in sandbox
# TYPE sandbox_files gauge
sandbox_files {len(list(SANDBOX_DIR.glob('*')))}
"""


if __name__ == '__main__':
    port = int(os.getenv('PORT', CONFIG['server']['port']))
    host = os.getenv('HOST', CONFIG['server']['host'])
    
    logger.info(f"Starting LocalAgent-Pro on {host}:{port}")
    logger.info(f"Ollama: {OLLAMA_BASE_URL}")
    logger.info(f"Model: {OLLAMA_MODEL}")
    logger.info(f"Sandbox: {SANDBOX_DIR}")
    
    app.run(host=host, port=port, debug=CONFIG['server']['debug'])
