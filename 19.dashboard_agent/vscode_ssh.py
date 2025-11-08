"""
VSCode SSH Integration Module
Handles secure SSH connections to remote servers for file operations
"""

import asyncssh
import logging
import asyncio
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VSCodeSSH:
    """SSH client wrapper for VS Code remote operations"""

    def __init__(self, host: str, user: str, key_path: str):
        self.host = host
        self.user = user
        self.key_path = key_path
        self._conn: Optional[asyncssh.SSHClientConnection] = None
        self._connected = False

    async def connect(self) -> bool:
        """Establish SSH connection"""
        try:
            self._conn = await asyncio.wait_for(
                asyncssh.connect(
                    self.host,
                    username=self.user,
                    client_keys=[self.key_path],
                    known_hosts=None,  # For testing; production: use known_hosts file
                    password=None,
                ),
                timeout=10
            )
            self._connected = True
            logger.info(f"✅ SSH connected to {self.host}")
            return True
        except asyncio.TimeoutError:
            logger.error(f"❌ SSH connection timeout to {self.host}")
            return False
        except Exception as e:
            logger.error(f"❌ SSH connection failed: {e}")
            return False

    async def exec_cmd(self, cmd: str, timeout: int = 30) -> str:
        """Execute shell command on remote server"""
        if not self._connected or not self._conn:
            raise RuntimeError("SSH connection not established")

        try:
            result = await asyncio.wait_for(
                self._conn.run(cmd, check=False),
                timeout=timeout
            )
            output = result.stdout.decode('utf-8', errors='ignore')
            if result.stderr:
                logger.warning(f"SSH stderr: {result.stderr.decode('utf-8', errors='ignore')}")
            return output
        except asyncio.TimeoutError:
            raise TimeoutError(f"Command timeout: {cmd}")
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise

    async def read_file(self, path: str, max_size: int = 10_000_000) -> str:
        """Read file from remote server"""
        try:
            # First check file size
            size_result = await self.exec_cmd(f"wc -c < {path}")
            size = int(size_result.strip())
            
            if size > max_size:
                raise ValueError(f"File too large: {size} bytes (max: {max_size})")
            
            content = await self.exec_cmd(f"cat {path}")
            logger.info(f"✅ Read {len(content)} bytes from {path}")
            return content
        except Exception as e:
            logger.error(f"❌ Failed to read {path}: {e}")
            raise

    async def write_file(self, path: str, content: str) -> bool:
        """Write file to remote server"""
        try:
            # Escape special characters for shell
            escaped_content = content.replace('\\', '\\\\').replace('"', '\\"')
            
            # Use heredoc for safe multi-line writes
            cmd = f'cat > {path} << \'EOF\'\n{content}\nEOF'
            
            await self.exec_cmd(cmd)
            logger.info(f"✅ Wrote {len(content)} bytes to {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write {path}: {e}")
            raise

    async def list_dir(self, path: str) -> list:
        """List directory contents"""
        try:
            result = await self.exec_cmd(f"ls -lah {path}")
            lines = result.strip().split('\n')[1:]  # Skip header
            
            files = []
            for line in lines:
                if line.strip():
                    parts = line.split(None, 8)
                    if len(parts) >= 9:
                        files.append({
                            "name": parts[8],
                            "type": "dir" if parts[0].startswith('d') else "file",
                            "size": parts[4],
                            "modified": f"{parts[5]} {parts[6]} {parts[7]}"
                        })
            
            logger.info(f"✅ Listed {len(files)} items in {path}")
            return files
        except Exception as e:
            logger.error(f"❌ Failed to list {path}: {e}")
            raise

    async def delete_file(self, path: str) -> bool:
        """Delete file from remote server"""
        try:
            await self.exec_cmd(f"rm -f {path}")
            logger.info(f"✅ Deleted {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete {path}: {e}")
            raise

    async def create_dir(self, path: str) -> bool:
        """Create directory on remote server"""
        try:
            await self.exec_cmd(f"mkdir -p {path}")
            logger.info(f"✅ Created directory {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create {path}: {e}")
            raise

    async def file_exists(self, path: str) -> bool:
        """Check if file exists on remote server"""
        try:
            result = await self.exec_cmd(f"test -f {path} && echo 'yes' || echo 'no'")
            return result.strip() == 'yes'
        except Exception as e:
            logger.error(f"❌ Failed to check {path}: {e}")
            return False

    async def close(self):
        """Close SSH connection"""
        if self._conn:
            self._conn.close()
            self._connected = False
            logger.info("✅ SSH connection closed")

    def is_connected(self) -> bool:
        """Check if SSH connection is active"""
        return self._connected and self._conn is not None


# Global SSH instance (will be initialized in main_opena4_vscode.py)
_ssh_instance: Optional[VSCodeSSH] = None


async def get_ssh() -> VSCodeSSH:
    """Get or create SSH instance"""
    global _ssh_instance
    if _ssh_instance is None:
        raise RuntimeError("SSH instance not initialized")
    return _ssh_instance


async def init_ssh(host: str, user: str, key_path: str) -> VSCodeSSH:
    """Initialize SSH instance"""
    global _ssh_instance
    _ssh_instance = VSCodeSSH(host, user, key_path)
    if not await _ssh_instance.connect():
        raise RuntimeError("Failed to initialize SSH connection")
    return _ssh_instance
