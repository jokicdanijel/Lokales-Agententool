#!/usr/bin/env python3
"""
ELION VSCode Programming Agent (opena5)
ELION Hyper-Dashboard 2.0 Integration

Funktionen:
- VSCode Integration und Programmier-Unterstützung  
- Code-Editing und Projekt-Management
- Git-Integration und Version Control
- Code-Analyse und Refactoring
- IntelliSense und Auto-Completion

Port: 12351
Autor: ELION Team
Version: 2.0
Datum: 29. November 2025
"""

import os
import asyncio
import json
import subprocess
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import httpx
import uvicorn


# ===== CONFIGURATION =====
class Config:
    AGENT_NAME = "opena5"
    AGENT_PORT = 12351
    DASHBOARD_URL = "http://127.0.0.1:12349"
    BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")
    
    # VSCode Paths
    WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")
    VSCODE_CONFIG_PATH = os.path.join(WORKSPACE_ROOT, ".vscode")
    GIT_ROOT = WORKSPACE_ROOT


# ===== PYDANTIC MODELS =====
class AgentHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: str
    agent: str
    port: int
    capabilities: List[str]
    vscode_integration: Dict[str, Any]
    timestamp: str


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    command: str
    target: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class VSCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    action: str  # "edit_file", "create_project", "git_commit", "analyze_code"
    file_path: Optional[str] = None
    code_content: Optional[str] = None
    project_type: Optional[str] = None
    commit_message: Optional[str] = None


class VSCodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    success: bool
    action: str
    result: Dict[str, Any]
    vscode_output: Optional[str] = None
    git_status: Optional[str] = None
    timestamp: str


# ===== SECURITY =====
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != Config.BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return credentials.credentials


# ===== VSCODE INTEGRATION =====
class VSCodeIntegration:
    """VSCode Integration und Programming Support"""
    
    def __init__(self):
        self.workspace_root = Config.WORKSPACE_ROOT
        self.vscode_config = Config.VSCODE_CONFIG_PATH
        self.git_root = Config.GIT_ROOT
        
    async def get_workspace_status(self) -> Dict[str, Any]:
        """Aktuelle Workspace-Status abrufen"""
        try:
            # VSCode Workspace prüfen
            vscode_exists = os.path.exists(self.vscode_config)
            
            # Git Status
            git_status = await self._get_git_status()
            
            # Projekt-Dateien zählen
            file_count = await self._count_project_files()
            
            return {
                "workspace_root": self.workspace_root,
                "vscode_config_exists": vscode_exists,
                "git_status": git_status,
                "project_files": file_count,
                "status": "ready"
            }
            
        except Exception as e:
            return {
                "workspace_root": self.workspace_root,
                "error": str(e),
                "status": "error"
            }
    
    async def edit_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Datei bearbeiten/erstellen"""
        try:
            full_path = os.path.join(self.workspace_root, file_path)
            
            # Verzeichnis erstellen falls nötig
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Backup erstellen bei existierender Datei
            backup_created = False
            if os.path.exists(full_path):
                backup_path = f"{full_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(full_path, backup_path)
                backup_created = True
            
            # Neue Datei schreiben
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "action": "edit_file",
                "file_path": file_path,
                "full_path": full_path,
                "backup_created": backup_created,
                "size_bytes": len(content.encode('utf-8')),
                "success": True
            }
            
        except Exception as e:
            return {
                "action": "edit_file",
                "file_path": file_path,
                "error": str(e),
                "success": False
            }
    
    async def create_project(self, project_type: str, project_name: str) -> Dict[str, Any]:
        """Neues Projekt erstellen"""
        try:
            project_path = os.path.join(self.workspace_root, project_name)
            
            if os.path.exists(project_path):
                return {
                    "action": "create_project",
                    "error": f"Project {project_name} already exists",
                    "success": False
                }
            
            # Projekt-Struktur erstellen
            os.makedirs(project_path, exist_ok=True)
            
            if project_type == "python":
                await self._create_python_project(project_path, project_name)
            elif project_type == "fastapi":
                await self._create_fastapi_project(project_path, project_name)
            elif project_type == "react":
                await self._create_react_project(project_path, project_name)
            else:
                await self._create_generic_project(project_path, project_name)
            
            return {
                "action": "create_project",
                "project_type": project_type,
                "project_name": project_name,
                "project_path": project_path,
                "success": True
            }
            
        except Exception as e:
            return {
                "action": "create_project",
                "error": str(e),
                "success": False
            }
    
    async def git_commit(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Git Commit durchführen"""
        try:
            os.chdir(self.git_root)
            
            # Dateien hinzufügen
            if files:
                for file in files:
                    subprocess.run(["git", "add", file], check=True)
            else:
                subprocess.run(["git", "add", "."], check=True)
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Status nach Commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, 
                text=True
            )
            
            return {
                "action": "git_commit",
                "message": message,
                "files_committed": files or "all",
                "git_output": result.stdout,
                "remaining_changes": len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0,
                "success": True
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "action": "git_commit",
                "error": f"Git error: {e.stderr}",
                "success": False
            }
        except Exception as e:
            return {
                "action": "git_commit",
                "error": str(e),
                "success": False
            }
    
    async def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Code-Analyse durchführen"""
        try:
            full_path = os.path.join(self.workspace_root, file_path)
            
            if not os.path.exists(full_path):
                return {
                    "action": "analyze_code",
                    "error": f"File not found: {file_path}",
                    "success": False
                }
            
            # Datei-Informationen
            stat = os.stat(full_path)
            
            # Code lesen und analysieren
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basis-Analyse
            analysis = {
                "file_path": file_path,
                "size_bytes": stat.st_size,
                "lines": len(content.split('\n')),
                "characters": len(content),
                "file_type": os.path.splitext(file_path)[1],
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # Sprachspezifische Analyse
            if file_path.endswith('.py'):
                analysis.update(await self._analyze_python_code(content))
            elif file_path.endswith(('.js', '.ts')):
                analysis.update(await self._analyze_javascript_code(content))
            
            return {
                "action": "analyze_code", 
                "analysis": analysis,
                "success": True
            }
            
        except Exception as e:
            return {
                "action": "analyze_code",
                "error": str(e),
                "success": False
            }
    
    # Helper Methods
    async def _get_git_status(self) -> Dict[str, Any]:
        """Git Status abrufen"""
        try:
            os.chdir(self.git_root)
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, 
                text=True
            )
            
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "has_changes": len(changes) > 0,
                "change_count": len(changes),
                "changes": changes[:10]  # Max 10 changes anzeigen
            }
        except:
            return {"has_changes": False, "change_count": 0, "error": "No git repository"}
    
    async def _count_project_files(self) -> Dict[str, int]:
        """Projekt-Dateien zählen"""
        try:
            counts = {"total": 0, "python": 0, "javascript": 0, "other": 0}
            
            for root, dirs, files in os.walk(self.workspace_root):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    counts["total"] += 1
                    
                    if file.endswith('.py'):
                        counts["python"] += 1
                    elif file.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        counts["javascript"] += 1
                    else:
                        counts["other"] += 1
                        
            return counts
        except:
            return {"total": 0, "python": 0, "javascript": 0, "other": 0}
    
    async def _create_python_project(self, path: str, name: str):
        """Python-Projekt erstellen"""
        # Hauptdatei
        with open(os.path.join(path, "main.py"), 'w') as f:
            f.write(f'#!/usr/bin/env python3\n"""\n{name}\n"""\n\ndef main():\n    print("Hello from {name}!")\n\nif __name__ == "__main__":\n    main()\n')
        
        # Requirements
        with open(os.path.join(path, "requirements.txt"), 'w') as f:
            f.write("# Add your dependencies here\n")
        
        # README
        with open(os.path.join(path, "README.md"), 'w') as f:
            f.write(f"# {name}\n\nPython project created by ELION VSCode Agent\n")
    
    async def _create_fastapi_project(self, path: str, name: str):
        """FastAPI-Projekt erstellen"""
        # Hauptdatei
        with open(os.path.join(path, "main.py"), 'w') as f:
            f.write(f'from fastapi import FastAPI\n\napp = FastAPI(title="{name}")\n\n@app.get("/")\nasync def root():\n    return {{"message": "Hello from {name}!"}}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n')
        
        # Requirements
        with open(os.path.join(path, "requirements.txt"), 'w') as f:
            f.write("fastapi==0.104.1\nuvicorn[standard]==0.24.0\n")
    
    async def _create_react_project(self, path: str, name: str):
        """React-Projekt erstellen (Basis)"""
        # Package.json
        package_json = {
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": f"React project created by ELION VSCode Agent",
            "main": "index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            },
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "react-scripts": "5.0.1"
            }
        }
        
        with open(os.path.join(path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
    
    async def _create_generic_project(self, path: str, name: str):
        """Generisches Projekt erstellen"""
        with open(os.path.join(path, "README.md"), 'w') as f:
            f.write(f"# {name}\n\nProject created by ELION VSCode Agent\n")
    
    async def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Python-Code analysieren"""
        return {
            "language": "python",
            "imports": len([line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]),
            "functions": content.count('def '),
            "classes": content.count('class '),
            "comments": len([line for line in content.split('\n') if line.strip().startswith('#')])
        }
    
    async def _analyze_javascript_code(self, content: str) -> Dict[str, Any]:
        """JavaScript-Code analysieren"""
        return {
            "language": "javascript",
            "functions": content.count('function ') + content.count('=>'),
            "imports": len([line for line in content.split('\n') if 'import' in line]),
            "exports": len([line for line in content.split('\n') if 'export' in line]),
            "comments": len([line for line in content.split('\n') if line.strip().startswith('//')])
        }


# ===== GLOBAL INSTANCES =====
vscode_integration = VSCodeIntegration()


# ===== DASHBOARD INTEGRATION =====
async def register_with_dashboard():
    """Agent beim Dashboard registrieren"""
    try:
        registration_data = {
            "agent_id": Config.AGENT_NAME,
            "name": "VSCode Programming Agent",
            "endpoint": f"http://127.0.0.1:{Config.AGENT_PORT}",
            "port": Config.AGENT_PORT,
            "capabilities": ["vscode", "programming", "code_editing", "project_management", "git_integration"],
            "status": "active",
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{Config.DASHBOARD_URL}/api/agent/register",
                json=registration_data,
                headers={"Authorization": f"Bearer {Config.BEARER_TOKEN}"},
                timeout=10.0
            )
            
        if response.status_code == 200:
            print(f"✅ Agent {Config.AGENT_NAME} registered with dashboard")
        else:
            print(f"⚠️ Dashboard registration failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Dashboard registration error: {e}")


async def publish_sse_event(event_type: str, data: dict):
    """SSE Event an Dashboard senden"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{Config.DASHBOARD_URL}/api/sse/publish",
                json={"event_type": event_type, "data": data},
                headers={"Authorization": f"Bearer {Config.BEARER_TOKEN}"},
                timeout=5.0
            )
    except Exception as e:
        print(f"SSE publish error: {e}")


# ===== FASTAPI APP =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle management"""
    print(f"🚀 Starting ELION VSCode Agent on port {Config.AGENT_PORT}")
    
    # Startup
    await register_with_dashboard()
    
    yield
    
    # Shutdown
    print("🛑 VSCode Agent shutting down")


app = FastAPI(
    title="ELION VSCode Programming Agent",
    description="VSCode Integration und Programmier-Unterstützung für ELION Hyper-Dashboard 2.0",
    version="2.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:12349", "http://localhost:12349"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ===== API ENDPOINTS =====
@app.get("/health", response_model=AgentHealth)
async def health_check():
    """Agent Health Check"""
    workspace_status = await vscode_integration.get_workspace_status()
    
    return AgentHealth(
        status="healthy",
        agent=Config.AGENT_NAME,
        port=Config.AGENT_PORT,
        capabilities=["vscode", "programming", "code_editing", "project_management", "git_integration"],
        vscode_integration=workspace_status,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/command", dependencies=[Depends(verify_token)])
async def handle_command(request: CommandRequest, background_tasks: BackgroundTasks):
    """Option-2 Command Interface"""
    try:
        # SSE Event für Command Start
        await publish_sse_event("command_received", {
            "agent": Config.AGENT_NAME,
            "command": request.command,
            "target": request.target
        })
        
        # Command verarbeiten
        if request.command == "vscode_status":
            result = await vscode_integration.get_workspace_status()
        elif request.command == "edit_file":
            result = await vscode_integration.edit_file(
                request.params.get("file_path", ""),
                request.params.get("content", "")
            )
        elif request.command == "create_project":
            result = await vscode_integration.create_project(
                request.params.get("project_type", "generic"),
                request.params.get("project_name", "new_project")
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown command: {request.command}")
        
        # SSE Event für Command Complete
        background_tasks.add_task(
            publish_sse_event, 
            "command_completed", 
            {"agent": Config.AGENT_NAME, "command": request.command, "success": True}
        )
        
        return {
            "success": True,
            "agent": Config.AGENT_NAME,
            "command": request.command,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        # SSE Event für Command Error
        background_tasks.add_task(
            publish_sse_event,
            "command_error",
            {"agent": Config.AGENT_NAME, "command": request.command, "error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vscode/action", response_model=VSCodeResponse, dependencies=[Depends(verify_token)])
async def vscode_action(request: VSCodeRequest, background_tasks: BackgroundTasks):
    """Direct VSCode Action Interface"""
    try:
        if request.action == "edit_file":
            result = await vscode_integration.edit_file(request.file_path, request.code_content)
        elif request.action == "create_project":
            result = await vscode_integration.create_project(request.project_type, request.file_path)
        elif request.action == "git_commit":
            result = await vscode_integration.git_commit(request.commit_message)
        elif request.action == "analyze_code":
            result = await vscode_integration.analyze_code(request.file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        # SSE Event
        background_tasks.add_task(
            publish_sse_event,
            "vscode_action", 
            {"agent": Config.AGENT_NAME, "action": request.action, "success": result.get("success", True)}
        )
        
        return VSCodeResponse(
            success=result.get("success", True),
            action=request.action,
            result=result,
            vscode_output=result.get("git_output"),
            git_status=result.get("git_status"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        return VSCodeResponse(
            success=False,
            action=request.action,
            result={"error": str(e)},
            timestamp=datetime.now(timezone.utc).isoformat()
        )


@app.get("/workspace/status", dependencies=[Depends(verify_token)])
async def workspace_status():
    """Workspace Status abrufen"""
    return await vscode_integration.get_workspace_status()


if __name__ == "__main__":
    uvicorn.run(
        "main_opena5:app",
        host="127.0.0.1",
        port=Config.AGENT_PORT,
        reload=False,
        log_level="info"
    )