# 🟣 Portier HyperSuite – Copilot Master Instructions

You are GitHub Copilot assisting in the development of the **Portier HyperSuite** for LocalAgentPro & OpenWebUI integration.

## Project Components

The Portier Suite consists of these production-ready modules:

- **Portier HyperDashboard 3.0.0** (Admin Version)
- **Portier Dashboard User 1.0.0** (User Version)
- **Portier Workflow Builder 1.0.0** (KI-Automation System)
- **Portier Monitoring Engine 1.0.0** (Live Metrics & Health)
- **Portier BrowserAgent Recorder 1.0.0** (Session Recording & Playback)
- **Portier PDF Viewer Tool** (Base64 Sandbox)
- **Portier Dispatcher FlowMap Tool** (Flow Visualization)
- **Portier Theme Pack** (5 Professional Themes)
- **Portier Installer Suite** (systemd, autostart, backups, recovery)

## Core Directives

### 1. Code Integrity

- **Never guess.** Always work strictly inside the existing codebase.
- **Scan files BEFORE writing** new code.
- **Modify only needed files.** Do not create unnecessary files.
- **Always verify file paths, imports and directories** before writing.
- **Use absolute Linux paths exactly** as referenced:

  ```
  /usr/local/portier/...
  /opt/open-webui/extensions/functions/...
  /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/...
  ```

### 2. OpenWebUI Compatibility

- **Maintain full compatibility** with OpenWebUI Tool architecture.
- **Tools class structure must be present** in every module.
- **All methods must be async-ready** (can be sync, but allow async).
- **Return format must be JSON-compatible** dict.
- **Pydantic models for type hints** (BaseModel, Field).

### 3. Module Structure

When adding new modules, follow this exact structure:

```
portier_<module_name>_x_x_x.py
├── Imports (pydantic, typing, os, etc)
├── Pydantic Models (data structures)
├── Tools class
│   └── @staticmethod methods
│       ├── Docstrings (comprehensive)
│       ├── Type hints (full coverage)
│       └── Return dict with {"status": "success", ...}
└── Mock data for development/offline mode
```

Example method signature:

```python
@staticmethod
def tool_action(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Action description

    Args:
        param1: Description
        param2: Description (default 10)

    Returns:
        Result dict with status and data
    """
    return {
        "status": "success",
        "data": {},
        "message": "..."
    }
```

### 4. Dashboard Architecture

#### Admin Dashboard (3.0.0)

- ✅ **No user mode** – unrestricted access
- ✅ **No restrictions** – all functions visible
- ✅ **No access control** – full feature visibility
- ✅ **Full system access** – all operations allowed

#### User Dashboard (1.0.0)

- ✅ **No admin functions** – cannot delete/edit system settings
- ✅ **Simplified navigation** – 4-6 core pages only
- ✅ **Safe actions only** – invoice generation, document viewing
- ✅ **Read-only integrations** – cannot modify integrations

### 5. Implementation Rules

#### When adding new modules

1. Create `portier_<name>_x_x_x.py` with full Tools class
2. Add to `FILES_TO_INSTALL` in `install_portier_dashboards.sh`
3. Add syntax check to installer script
4. Test via `python3 -m py_compile`

#### When updating the Installer

1. Add new modules to copy+validation routine
2. Integrate with existing backup system
3. Update next steps documentation
4. Maintain backward compatibility

#### When modifying tools

1. Maintain full async compatibility
2. Do not break existing OpenWebUI interfaces
3. Keep return format consistent
4. Preserve type hints and docstrings

#### When building UI features

Use unified JSON structure:

```json
{
  "theme": {},
  "navigation": [],
  "page": "page_name",
  "content": {
    "title": "...",
    "widgets": [],
    "data": {}
  }
}
```

### 6. File Path Management

**Never hallucinate paths.** Use ONLY these verified locations:

**Portier Suite Directory:**

```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/OpenWebUI-Portier/
```

**OpenWebUI Target Directory:**

```
./open-webui/extensions/functions/
```

**Portier System Directories (when needed):**

```
/usr/local/portier/workflows/
/usr/local/portier/logs/
/usr/local/portier/backups/
/usr/local/portier/recovery/
/usr/local/portier/config/
```

### 7. Validation Rules

Before finalizing any code:

1. **Python Syntax Check:**

   ```bash
   python3 -m py_compile portier_module_x_x_x.py
   ```

2. **Pydantic Models:**
   - All data structures inherit from `BaseModel`
   - Use `Field` for default values and descriptions
   - Type hints on all fields

3. **Tools Class Methods:**
   - All methods are `@staticmethod`
   - All methods have docstrings
   - All methods return `Dict[str, Any]`
   - All methods include status field

4. **Documentation:**
   - Docstrings with Args, Returns sections
   - Type hints on all parameters
   - Comments for complex logic

### 8. Error Handling

Always implement graceful error handling:

```python
try:
    # Main logic
    result = perform_action()
    return {
        "status": "success",
        "data": result,
        "message": "Action completed"
    }
except SpecificError as e:
    return {
        "status": "error",
        "message": f"Error description: {str(e)}",
        "error_code": "ERROR_CODE"
    }
except Exception as e:
    return {
        "status": "error",
        "message": "Unexpected error",
        "error": str(e)
    }
```

### 9. User vs Admin Separation

**Important:** User and Admin dashboards are COMPLETELY separate:

#### Admin Dashboard Features

- User management (CRUD)
- System settings
- Backup/restore
- Audit logging
- Service control
- Resource monitoring
- Role management

#### User Dashboard Features

- Invoices (view, generate, export)
- Documents (upload, view, analyze)
- Integrations (view status only)
- Personal dashboard
- Profile settings

### 10. Testing & Quality Assurance

Before considering any module complete:

1. ✅ Syntax validation passes
2. ✅ Pydantic models validated
3. ✅ All methods documented
4. ✅ Type hints complete
5. ✅ Error handling in place
6. ✅ Mock data for offline use
7. ✅ Return format consistent
8. ✅ OpenWebUI compatibility verified

## Expected Behavior

### When user asks: "Build X"

→ Generate complete code in correct file format + add to installer

### When user asks: "Integrate X into installer"

→ Patch `install_portier_dashboards.sh` appropriately

### When user asks: "Add new tool"

→ Create complete OpenWebUI Tool code with Tools class + models

### When user asks: "Fix [issue]"

→ Identify broken code segments + provide corrections

### When user asks: "Extend dashboard"

→ Patch correct dashboard file (user or admin) without breaking existing code

### When user asks: "Create theme"

→ Add to `theme_pack.json` with all required fields

### When user asks: "Update docs"

→ Modify README.md or create installation guide

## Golden Rules

1. ✅ **Scan first, generate second** – always read existing code
2. ✅ **Structure before coding** – plan architecture first
3. ✅ **Validate always** – py_compile every Python file
4. ✅ **Never overwrite** – always backup before modifying
5. ✅ **Paths are sacred** – never invent file locations
6. ✅ **JSON is king** – all returns must be JSON-serializable
7. ✅ **Async-ready** – design for async/await patterns
8. ✅ **Tools class mandatory** – every module needs Tools class
9. ✅ **Type hints required** – full type coverage expected
10. ✅ **Documentation matters** – docstrings are not optional

## Module Checklist

For every new module, verify:

- [ ] `portier_<name>_x_x_x.py` created
- [ ] Pydantic models defined
- [ ] Tools class with @staticmethod methods
- [ ] All methods have docstrings
- [ ] Type hints on all parameters and returns
- [ ] Error handling implemented
- [ ] Mock data for offline mode
- [ ] Syntax validation passes
- [ ] Added to install script
- [ ] README updated with usage examples
- [ ] OpenWebUI compatibility tested

## Current Module Status

✅ **Deployed & Validated:**

- Portier HyperDashboard 3.0.0
- Portier Dashboard User 1.0.0
- Portier Workflow Builder 1.0.0
- Portier Monitoring Engine 1.0.0
- Portier BrowserAgent Recorder 1.0.0
- Portier PDF Viewer 1.0.0
- Portier Dispatcher FlowMap 1.0.0
- Theme Pack (5 themes)
- Installer Suite

**Total:** 7 production modules + 1 theme pack + installer

## Next Steps When Needed

When extending the suite:

1. Analyze existing module structure
2. Create new module following template
3. Implement Tools class with all methods
4. Add Pydantic models for type safety
5. Include mock data
6. Validate syntax
7. Add to installer
8. Test OpenWebUI integration
9. Document in README
10. Mark as production-ready

---

**Version:** 1.0.0 (Final)
**Last Updated:** 2025-11-25
**Compatibility:** OpenWebUI 1.0+, Python 3.8+, Linux (any distro)
**Status:** Production Ready ✅
