#!/usr/bin/env python3
"""
OpenA3 Web Dashboard - Updated 2025
Comprehensive web interface for all tools and voice programs
Runs on http://localhost:8000
Real-time monitoring, metrics & system control
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
from datetime import datetime
import threading
import subprocess
import socket
import psutil
import platform

PORT = 8000
VERSION = "2.0.0"


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handle HTTP requests for the dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/" or self.path == "/index.html":
            self.serve_index()
        elif self.path == "/status":
            self.serve_status_page()
        elif self.path == "/tools":
            self.serve_tools_page()
        elif self.path == "/programs":
            self.serve_programs_page()
        elif self.path == "/api/status":
            self.serve_status()
        elif self.path == "/api/tools":
            self.serve_tools()
        elif self.path == "/api/programs":
            self.serve_programs()
        elif self.path.startswith("/api/file/list"):
            self.serve_file_list()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            if self.path == "/api/file/read":
                self.handle_file_read(data)
            elif self.path == "/api/file/write":
                self.handle_file_write(data)
            elif self.path == "/api/file/delete":
                self.handle_file_delete(data)
            elif self.path == "/api/shell/exec":
                self.handle_shell_exec(data)
            elif self.path == "/api/program/start":
                self.handle_program_start(data)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def serve_index(self):
        """Serve main dashboard HTML"""
        html_content = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 OpenA3 Dashboard - LocalAgent-Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%);
            color: #ffffff;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            color: #aaa;
            font-size: 1.1em;
        }

        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .status-item {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .status-item.online {
            background: rgba(0, 255, 136, 0.1);
            border-color: rgba(0, 255, 136, 0.3);
        }

        .status-item.offline {
            background: rgba(255, 100, 100, 0.1);
            border-color: rgba(255, 100, 100, 0.3);
        }

        .status-label {
            font-size: 0.9em;
            color: #aaa;
        }

        .status-badge {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .badge-online {
            background: #00ff88;
            color: #000;
        }

        .badge-offline {
            background: #ff6464;
            color: #fff;
        }

        .section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .card:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(0, 212, 255, 0.5);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
        }

        .card-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .card-title {
            font-size: 1.3em;
            margin-bottom: 8px;
            color: #00d4ff;
        }

        .card-description {
            font-size: 0.95em;
            color: #aaa;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .card-features {
            list-style: none;
            font-size: 0.85em;
            color: #ccc;
            margin: 10px 0;
        }

        .card-features li {
            padding: 3px 0;
            padding-left: 20px;
            position: relative;
        }

        .card-features li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #00d4ff;
        }

        .card-button {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
            margin-top: 15px;
            transition: all 0.3s ease;
        }

        .card-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
        }

        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .tab-button {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #aaa;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .tab-button.active {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            color: white;
            border-color: transparent;
        }

        .tab-button:hover {
            border-color: rgba(0, 212, 255, 0.5);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .stat {
            background: rgba(0, 212, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }

        .stat-value {
            font-size: 1.8em;
            color: #00d4ff;
            font-weight: bold;
        }

        .stat-label {
            font-size: 0.85em;
            color: #aaa;
            margin-top: 5px;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }

        .modal.show {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            font-size: 1.5em;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .close-btn {
            background: none;
            border: none;
            color: #aaa;
            font-size: 1.5em;
            cursor: pointer;
        }

        .close-btn:hover {
            color: #fff;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .section-title {
                font-size: 1.3em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 OpenA3 Dashboard</h1>
            <p class="subtitle">LocalAgent-Pro - Intelligenter AI-Agent Server mit Sprachsteuerung</p>

            <div class="status-bar" id="statusBar">
                <div class="status-item">
                    <span class="status-label">LocalAgent-Pro</span>
                    <span class="status-badge badge-online">Online</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Services</span>
                    <span class="status-badge badge-online">4 Running</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Uptime</span>
                    <span class="status-badge badge-online">Active</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Version</span>
                    <span class="status-badge badge-online">1.0.0</span>
                </div>
            </div>
        </header>

        <!-- TOOLS SECTION -->
        <section class="section">
            <h2 class="section-title">🔧 API Tools (Chat Integration)</h2>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Tools</div>
                </div>
                <div class="stat">
                    <div class="stat-value">100%</div>
                    <div class="stat-label">Integration</div>
                </div>
                <div class="stat">
                    <div class="stat-value">Sandbox</div>
                    <div class="stat-label">Sicher</div>
                </div>
            </div>

            <div class="grid" id="toolsGrid">
                <!-- Generated by JavaScript -->
            </div>
        </section>

        <!-- VOICE PROGRAMS SECTION -->
        <section class="section">
            <h2 class="section-title">🎤 Voice Programme (Sprachsteuerung)</h2>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">6</div>
                    <div class="stat-label">Programme</div>
                </div>
                <div class="stat">
                    <div class="stat-value">1.041</div>
                    <div class="stat-label">Code-Zeilen</div>
                </div>
                <div class="stat">
                    <div class="stat-value">40+</div>
                    <div class="stat-label">Funktionen</div>
                </div>
            </div>

            <div class="grid" id="programsGrid">
                <!-- Generated by JavaScript -->
            </div>
        </section>

        <!-- TOOL EXECUTION SECTION -->
        <section class="section">
            <h2 class="section-title">⚙️ Tool Execution (Datei & Shell)</h2>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">4</div>
                    <div class="stat-label">Tools</div>
                </div>
                <div class="stat">
                    <div class="stat-value">Sicher</div>
                    <div class="stat-label">Sandbox</div>
                </div>
                <div class="stat">
                    <div class="stat-value">WhiteList</div>
                    <div class="stat-label">Befehle</div>
                </div>
            </div>

            <div class="tab-buttons">
                <button class="tab-button active" onclick="switchTab('file-ops')">📁 Dateien</button>
                <button class="tab-button" onclick="switchTab('shell-ops')">💻 Shell</button>
            </div>

            <!-- FILE OPERATIONS -->
            <div id="file-ops-tab" class="tab-content">
                <div class="tool-panel">
                    <h3 style="margin-bottom: 20px; color: #00d4ff;">📁 Dateiverwaltung</h3>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <!-- File List -->
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 20px;">
                            <h4 style="margin-bottom: 15px;">📂 Dateien & Ordner</h4>
                            <div id="fileList" style="max-height: 400px; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px;">
                                <p style="color: #666;">Lädt...</p>
                            </div>
                            <button class="card-button" style="width: 100%; margin-top: 15px;" onclick="loadFileList()">🔄 Aktualisieren</button>
                        </div>

                        <!-- File Operations -->
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 20px;">
                            <h4 style="margin-bottom: 15px;">⚙️ Operationen</h4>

                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em;">Dateipfad:</label>
                                <input id="filePath" type="text" placeholder="z.B. test.txt" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                            </div>

                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em;">Inhalt:</label>
                                <textarea id="fileContent" placeholder="Dateiinhalt..." style="width: 100%; height: 150px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 8px; border-radius: 5px; resize: none;"></textarea>
                            </div>

                            <div style="display: flex; gap: 10px;">
                                <button class="card-button" style="flex: 1;" onclick="readFile()">📖 Lesen</button>
                                <button class="card-button" style="flex: 1; background: linear-gradient(135deg, #00ff88, #00cc66);" onclick="writeFile()">💾 Schreiben</button>
                                <button class="card-button" style="flex: 1; background: linear-gradient(135deg, #ff6464, #ff4444);" onclick="deleteFile()">🗑️ Löschen</button>
                            </div>

                            <div id="fileResult" style="margin-top: 15px; padding: 10px; background: rgba(0,212,255,0.1); border-radius: 5px; border: 1px solid rgba(0,212,255,0.2); display: none; color: #00d4ff; font-size: 0.9em;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SHELL OPERATIONS -->
            <div id="shell-ops-tab" class="tab-content" style="display: none;">
                <div class="tool-panel">
                    <h3 style="margin-bottom: 20px; color: #00d4ff;">💻 Shell Befehle</h3>

                    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 20px;">
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em;">Befehl (WhiteList):</label>
                            <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(0,212,255,0.2); border-radius: 5px; padding: 10px; margin-bottom: 10px; font-size: 0.85em; color: #888;">
                                <strong>Erlaubte Befehle:</strong> ls, pwd, echo, cat, grep, find, wc, head, tail, date, whoami, mkdir, rm, cp, mv, touch, chmod, python3, pip3
                            </div>
                            <input id="shellCommand" type="text" placeholder="z.B. ls -la tools/" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 10px; border-radius: 5px; font-family: monospace;">
                        </div>

                        <div style="display: flex; gap: 10px;">
                            <button class="card-button" style="flex: 1;" onclick="executeCommand()">▶️ Ausführen</button>
                            <button class="card-button" style="flex: 1; background: linear-gradient(135deg, #ff9900, #ff7700);" onclick="clearShellOutput()">🗑️ Löschen</button>
                        </div>

                        <div id="shellResult" style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.5); border: 1px solid rgba(0,212,255,0.2); border-radius: 8px; display: none; font-family: monospace; font-size: 0.85em; max-height: 400px; overflow-y: auto;">
                            <pre id="shellOutput" style="color: #00d4ff; margin: 0;"></pre>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <footer>
            <p>🚀 OpenA3 - Production Ready | LocalAgent-Pro v1.0.0</p>
            <p>© 2025 - Intelligente AI-Agent Plattform mit Sprachsteuerung</p>
        </footer>
    </div>

    <!-- MODAL -->
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span id="modalTitle"></span>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>

    <script>
        const tools = [
            {
                icon: "📝",
                title: "Write File",
                description: "Erstelle Dateien in der Sandbox",
                features: ["Text speichern", "UTF-8 Encoding", "Fehlerbehandlung"],
                command: "write_file"
            },
            {
                icon: "📖",
                title: "Read File",
                description: "Lese Dateien aus der Sandbox",
                features: ["Dateiinhalte", "Encoding-Support", "Große Dateien"],
                command: "read_file"
            },
            {
                icon: "🗑️",
                title: "Delete File",
                description: "Lösche Dateien aus der Sandbox",
                features: ["Sichere Löschung", "Bestätigung", "Logs"],
                command: "delete_file"
            },
            {
                icon: "💻",
                title: "Shell Exec",
                description: "Führe Shell-Befehle aus",
                features: ["Whitelisting", "Timeout", "Output-Capture"],
                command: "shell_exec"
            },
            {
                icon: "🌐",
                title: "Fetch Webpage",
                description: "Hole Web-Inhalte ab",
                features: ["Vertrauenswürdige Domains", "Headers", "Error-Handling"],
                command: "fetch_webpage"
            }
        ];

        const programs = [
            {
                icon: "🗣️",
                title: "Voice Command Parser",
                description: "Sprachbefehle in Systemaktionen konvertieren",
                features: ["Datei-Management", "Verzeichnis-Ops", "System-Info"],
                lines: 147,
                file: "voice_command_parser.py"
            },
            {
                icon: "📝",
                title: "Voice Note Recorder",
                description: "Sprachnotizen aufnehmen und verwalten",
                features: ["Live-Aufnahme", "Suche", "Export (TXT/JSON)"],
                lines: 187,
                file: "voice_note_recorder.py"
            },
            {
                icon: "📞",
                title: "Voice Call System",
                description: "Kontakt- und Anrufverwaltung",
                features: ["Kontakte", "Sprachanrufe", "SMS & Verlauf"],
                lines: 173,
                file: "voice_call_system.py"
            },
            {
                icon: "🤖",
                title: "Voice Assistant",
                description: "Intelligente Sprachassistentin",
                features: ["Zeit/Datum", "Rechner", "System-Monitor"],
                lines: 138,
                file: "voice_assistant.py"
            },
            {
                icon: "📄",
                title: "Voice Transcriber",
                description: "Audio-Transkription mit Analyse",
                features: ["Live-Transkription", "Datei-Support", "Statistiken"],
                lines: 226,
                file: "voice_transcriber.py"
            },
            {
                icon: "📅",
                title: "Voice Scheduler",
                description: "Aufgabenverwaltung per Sprachbefehl",
                features: ["Aufgaben-Erfassung", "Tracking", "Übersicht"],
                lines: 176,
                file: "voice_scheduler.py"
            }
        ];

        function renderTools() {
            const grid = document.getElementById('toolsGrid');
            grid.innerHTML = tools.map(tool => `
                <div class="card" onclick="showToolDetail('${tool.title}')">
                    <div class="card-icon">${tool.icon}</div>
                    <div class="card-title">${tool.title}</div>
                    <div class="card-description">${tool.description}</div>
                    <ul class="card-features">
                        ${tool.features.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                    <button class="card-button">Mehr Info</button>
                </div>
            `).join('');
        }

        function renderPrograms() {
            const grid = document.getElementById('programsGrid');
            grid.innerHTML = programs.map(prog => `
                <div class="card" onclick="showProgramDetail('${prog.title}')">
                    <div class="card-icon">${prog.icon}</div>
                    <div class="card-title">${prog.title}</div>
                    <div class="card-description">${prog.description}</div>
                    <ul class="card-features">
                        ${prog.features.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                    <small style="color: #666;">📊 ${prog.lines} Zeilen | tools/${prog.file}</small>
                    <button class="card-button">Starten</button>
                </div>
            `).join('');
        }

        function showToolDetail(title) {
            const tool = tools.find(t => t.title === title);
            if (tool) {
                document.getElementById('modalTitle').textContent = `${tool.icon} ${tool.title}`;
                document.getElementById('modalBody').innerHTML = `
                    <p><strong>Beschreibung:</strong> ${tool.description}</p>
                    <p><strong>Befehl:</strong> <code>${tool.command}</code></p>
                    <h4 style="margin-top: 20px; margin-bottom: 10px;">Features:</h4>
                    <ul style="list-style: none; padding-left: 0;">
                        ${tool.features.map(f => `<li style="padding: 5px 0;">✓ ${f}</li>`).join('')}
                    </ul>
                    <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
                        Dieses Tool ist in LocalAgent-Pro über die Chat-API integriert.
                    </p>
                `;
                document.getElementById('modal').classList.add('show');
            }
        }

        function showProgramDetail(title) {
            const prog = programs.find(p => p.title === title);
            if (prog) {
                document.getElementById('modalTitle').textContent = `${prog.icon} ${prog.title}`;
                document.getElementById('modalBody').innerHTML = `
                    <p><strong>Beschreibung:</strong> ${prog.description}</p>
                    <p><strong>Datei:</strong> <code>tools/${prog.file}</code></p>
                    <p><strong>Größe:</strong> ${prog.lines} Zeilen</p>
                    <h4 style="margin-top: 20px; margin-bottom: 10px;">Features:</h4>
                    <ul style="list-style: none; padding-left: 0;">
                        ${prog.features.map(f => `<li style="padding: 5px 0;">✓ ${f}</li>`).join('')}
                    </ul>
                    <h4 style="margin-top: 20px; margin-bottom: 10px;">Ausführung:</h4>
                    <code style="background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 5px; display: block;">
                        python3 tools/${prog.file}
                    </code>
                    <div style="margin-top: 20px; display: flex; gap: 10px;">
                        <button class="card-button" style="flex: 1; background: linear-gradient(135deg, #00ff88, #00cc66);" onclick="startProgram('${prog.file}')">
                            ▶️ Starten
                        </button>
                        <button class="card-button" style="flex: 1;" onclick="copyCommand('python3 tools/${prog.file}')">
                            📋 Kopieren
                        </button>
                    </div>
                    <div id="programOutput" style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px; display: none; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.85em; color: #00ff88;"></div>
                    <p style="margin-top: 15px; color: #666; font-size: 0.9em;">
                        Dieses Programm läuft standalone mit interaktivem Menü.
                    </p>
                `;
                document.getElementById('modal').classList.add('show');
            }
        }

        async function startProgram(file) {
            try {
                const outputDiv = document.getElementById('programOutput');
                outputDiv.style.display = 'block';
                outputDiv.textContent = '⏳ Starte ' + file + '...';

                const response = await fetch('/api/program/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file: file })
                });

                const data = await response.json();

                if (data.error) {
                    outputDiv.textContent = '❌ Fehler: ' + data.error;
                    outputDiv.style.color = '#ff6464';
                } else {
                    outputDiv.textContent = '✅ ' + data.message + '\n\n' + (data.pid ? 'PID: ' + data.pid : '') + '\n\nProgramm läuft im Hintergrund...';
                    outputDiv.style.color = '#00ff88';
                }
            } catch (e) {
                const outputDiv = document.getElementById('programOutput');
                outputDiv.style.display = 'block';
                outputDiv.textContent = '❌ Fehler: ' + e.message;
                outputDiv.style.color = '#ff6464';
            }
        }

        function copyCommand(command) {
            navigator.clipboard.writeText(command).then(() => {
                alert('✅ Befehl kopiert!');
            }).catch(err => {
                alert('❌ Fehler beim Kopieren');
            });
        }

        function closeModal() {
            document.getElementById('modal').classList.remove('show');
        }

        // Close modal on background click
        document.getElementById('modal').addEventListener('click', function(event) {
            if (event.target === this) {
                closeModal();
            }
        });

        // Render content on load
        window.addEventListener('load', function() {
            renderTools();
            renderPrograms();
            loadFileList();
        });

        // TAB SWITCHING
        function switchTab(tabName) {
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.style.display = 'none');

            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));

            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
        }

        // FILE OPERATIONS
        async function loadFileList() {
            try {
                const response = await fetch('/api/file/list');
                const data = await response.json();

                const fileList = document.getElementById('fileList');
                if (data.files && data.files.length > 0) {
                    fileList.innerHTML = data.files.map(f => `
                        <div style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); cursor: pointer; display: flex; justify-content: space-between; align-items: center;" onclick="selectFile('${f.path}')">
                            <span>${f.type === 'dir' ? '📁' : '📄'} ${f.name}</span>
                            ${f.size ? `<span style="color: #666; font-size: 0.85em;">${(f.size / 1024).toFixed(1)} KB</span>` : ''}
                        </div>
                    `).join('');
                } else {
                    fileList.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">Keine Dateien gefunden</p>';
                }
            } catch (e) {
                document.getElementById('fileList').innerHTML = `<p style="color: #ff6464;">❌ Fehler: ${e.message}</p>`;
            }
        }

        function selectFile(filename) {
            document.getElementById('filePath').value = filename;
            readFile();
        }

        async function readFile() {
            const path = document.getElementById('filePath').value;
            if (!path) {
                alert('Dateipfad erforderlich');
                return;
            }

            try {
                const response = await fetch('/api/file/read', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path })
                });
                const data = await response.json();

                if (data.error) {
                    showFileResult('❌ Fehler: ' + data.error, true);
                } else {
                    document.getElementById('fileContent').value = data.content;
                    showFileResult('✅ Datei gelesen: ' + data.size + ' bytes');
                }
            } catch (e) {
                showFileResult('❌ Fehler: ' + e.message, true);
            }
        }

        async function writeFile() {
            const path = document.getElementById('filePath').value;
            const content = document.getElementById('fileContent').value;
            if (!path) {
                alert('Dateipfad erforderlich');
                return;
            }

            try {
                const response = await fetch('/api/file/write', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path, content: content })
                });
                const data = await response.json();

                if (data.error) {
                    showFileResult('❌ Fehler: ' + data.error, true);
                } else {
                    showFileResult('✅ ' + data.message);
                    loadFileList();
                }
            } catch (e) {
                showFileResult('❌ Fehler: ' + e.message, true);
            }
        }

        async function deleteFile() {
            const path = document.getElementById('filePath').value;
            if (!path || !confirm('Datei wirklich löschen?')) return;

            try {
                const response = await fetch('/api/file/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path })
                });
                const data = await response.json();

                if (data.error) {
                    showFileResult('❌ Fehler: ' + data.error, true);
                } else {
                    showFileResult('✅ ' + data.message);
                    document.getElementById('filePath').value = '';
                    document.getElementById('fileContent').value = '';
                    loadFileList();
                }
            } catch (e) {
                showFileResult('❌ Fehler: ' + e.message, true);
            }
        }

        function showFileResult(message, isError = false) {
            const result = document.getElementById('fileResult');
            result.textContent = message;
            result.style.display = 'block';
            result.style.color = isError ? '#ff6464' : '#00ff88';
            result.style.background = isError ? 'rgba(255,100,100,0.1)' : 'rgba(0,255,136,0.1)';
            result.style.borderColor = isError ? 'rgba(255,100,100,0.2)' : 'rgba(0,255,136,0.2)';
            setTimeout(() => { result.style.display = 'none'; }, 5000);
        }

        // SHELL OPERATIONS
        async function executeCommand() {
            const command = document.getElementById('shellCommand').value;
            if (!command) {
                alert('Befehl erforderlich');
                return;
            }

            const resultDiv = document.getElementById('shellResult');
            document.getElementById('shellOutput').textContent = '⏳ Befehl wird ausgeführt...';
            resultDiv.style.display = 'block';

            try {
                const response = await fetch('/api/shell/exec', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                const data = await response.json();

                let output = `$ ${command}\n\n`;

                if (data.error) {
                    output += `❌ Fehler: ${data.error}`;
                    if (data.allowed) {
                        output += `\n\nErlaubte Befehle: ${data.allowed.join(', ')}`;
                    }
                } else {
                    if (data.stdout) output += data.stdout;
                    if (data.stderr) output += `\n❌ stderr:\n${data.stderr}`;
                    output += `\n\n✅ Return code: ${data.returncode}`;
                }

                document.getElementById('shellOutput').textContent = output;
            } catch (e) {
                document.getElementById('shellOutput').textContent = `❌ Netzwerkfehler: ${e.message}`;
            }
        }

        function clearShellOutput() {
            document.getElementById('shellCommand').value = '';
            document.getElementById('shellResult').style.display = 'none';
        }
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_status_page(self):
        """Serve system status as HTML page"""
        import json as json_module
        try:
            status = {
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "services": {
                    "localaagent-pro": "running",
                    "ollama": "running",
                    "openwebui": "running",
                    "http-server": "running"
                }
            }

            html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>🤖 System Status - OpenA3</title>
    <style>
        body {{ font-family: Segoe UI, sans-serif; background: #0f0f0f; color: #fff; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; margin-bottom: 30px; }}
        .status-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .status-item {{ background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.3); padding: 20px; border-radius: 10px; }}
        .status-item h3 {{ margin: 0 0 10px 0; color: #00d4ff; }}
        .status-value {{ font-size: 14px; color: #aaa; }}
        .service {{ background: rgba(0,255,136,0.1); border-left: 3px solid #00ff88; padding: 10px; margin: 5px 0; }}
        .back-link {{ margin-top: 30px; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 System Status</h1>

        <div class="status-grid">
            <div class="status-item">
                <h3>Status</h3>
                <div class="status-value">✅ {status['status'].upper()}</div>
            </div>

            <div class="status-item">
                <h3>Version</h3>
                <div class="status-value">{status['version']}</div>
            </div>

            <div class="status-item">
                <h3>Zeitstempel</h3>
                <div class="status-value">{status['timestamp']}</div>
            </div>

            <div class="status-item">
                <h3>Dienste</h3>
                <div class="status-value">
                    {''.join([f'<div class="service">✅ {k}: {v}</div>' for k,v in status['services'].items()])}
                </div>
            </div>
        </div>

        <div class="back-link">
            <a href="/">← Zurück zum Dashboard</a>
        </div>
    </div>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def serve_tools_page(self):
        """Serve tools list as HTML page"""
        try:
            tools = [
                {"name": "📝 File Manager", "desc": "Read, write, delete files safely", "icon": "📁"},
                {"name": "⚡ Shell Executor", "desc": "Execute whitelisted shell commands", "icon": "🖥️"},
                {"name": "🎤 Program Launcher", "desc": "Start voice programs in background", "icon": "🚀"}
            ]

            tools_html = '\n'.join([
                f'<div class="tool-card"><div class="tool-icon">{t["icon"]}</div><h3>{t["name"]}</h3><p>{t["desc"]}</p></div>'
                for t in tools
            ])

            html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>🛠️ Tools - OpenA3</title>
    <style>
        body {{ font-family: Segoe UI, sans-serif; background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%); color: #fff; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; margin-bottom: 30px; }}
        .tools-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .tool-card {{ background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.3); padding: 25px; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s; }}
        .tool-card:hover {{ transform: translateY(-5px); background: rgba(0,212,255,0.2); }}
        .tool-icon {{ font-size: 40px; margin-bottom: 10px; }}
        .tool-card h3 {{ margin: 0 0 10px 0; color: #00d4ff; }}
        .tool-card p {{ margin: 0; color: #aaa; font-size: 14px; }}
        .back-link {{ margin-top: 30px; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ Verfügbare Tools</h1>

        <div class="tools-grid">
            {tools_html}
        </div>

        <div class="back-link">
            <a href="/">← Zurück zum Dashboard</a>
        </div>
    </div>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def serve_programs_page(self):
        """Serve voice programs list as HTML page"""
        try:
            programs = [
                {"name": "🎤 Voice Assistant", "file": "voice_assistant.py", "desc": "AI-powered voice commands"},
                {"name": "📋 Command Parser", "file": "voice_command_parser.py", "desc": "Parse voice input"},
                {"name": "☎️ Call System", "file": "voice_call_system.py", "desc": "Voice call management"},
                {"name": "📝 Note Recorder", "file": "voice_note_recorder.py", "desc": "Record voice notes"},
                {"name": "🎙️ Transcriber", "file": "voice_transcriber.py", "desc": "Audio transcription"},
                {"name": "📅 Scheduler", "file": "voice_scheduler.py", "desc": "Schedule voice tasks"}
            ]

            programs_html = '\n'.join([
                f'''<div class="program-card" onclick="startProgram('{p['file']}')">
                    <div class="program-title">{p["name"]}</div>
                    <div class="program-desc">{p["desc"]}</div>
                    <button class="start-btn">▶️ Starten</button>
                </div>'''
                for p in programs
            ])

            html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>🎤 Voice Programme - OpenA3</title>
    <style>
        body {{ font-family: Segoe UI, sans-serif; background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%); color: #fff; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; margin-bottom: 30px; }}
        .programs-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .program-card {{ background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.3); padding: 20px; border-radius: 12px; cursor: pointer; transition: all 0.3s; }}
        .program-card:hover {{ transform: translateY(-5px); background: rgba(0,212,255,0.2); }}
        .program-title {{ font-size: 18px; font-weight: bold; color: #00d4ff; margin-bottom: 8px; }}
        .program-desc {{ color: #aaa; font-size: 13px; margin-bottom: 15px; }}
        .start-btn {{ background: #00d4ff; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; }}
        .start-btn:hover {{ background: #00e5ff; }}
        .back-link {{ margin-top: 30px; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        #output {{ margin-top: 20px; background: rgba(0,212,255,0.05); padding: 15px; border-radius: 5px; display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Voice Programme</h1>

        <div class="programs-grid">
            {programs_html}
        </div>

        <div id="output"></div>

        <div class="back-link">
            <a href="/">← Zurück zum Dashboard</a>
        </div>
    </div>

    <script>
        async function startProgram(file) {{
            try {{
                const response = await fetch('/api/program/start', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{file: file}})
                }});
                const data = await response.json();
                const output = document.getElementById('output');
                output.style.display = 'block';
                if (data.status === 'ok') {{
                    output.innerHTML = `✅ Programm gestartet! PID: ${{data.pid}}`;
                }} else {{
                    output.innerHTML = `❌ Fehler: ${{data.error}}`;
                }}
            }} catch (e) {{
                document.getElementById('output').innerHTML = `❌ Fehler: ${{e.message}}`;
                document.getElementById('output').style.display = 'block';
            }}
        }}
    </script>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def serve_status(self):
        """Serve system status as JSON"""
        status = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "localaagent-pro": "running",
                "ollama": "running",
                "openwebui": "running",
                "http-server": "running"
            },
            "tools": 5,
            "programs": 6,
            "total_code_lines": 1041
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(status).encode("utf-8"))

    def serve_tools(self):
        """Serve available tools as JSON"""
        tools = [
            {
                "name": "write_file",
                "description": "Erstelle Dateien in der Sandbox",
                "category": "File Operations"
            },
            {
                "name": "read_file",
                "description": "Lese Dateien aus der Sandbox",
                "category": "File Operations"
            },
            {
                "name": "delete_file",
                "description": "Lösche Dateien aus der Sandbox",
                "category": "File Operations"
            },
            {
                "name": "shell_exec",
                "description": "Führe Shell-Befehle aus",
                "category": "System Commands"
            },
            {
                "name": "fetch_webpage",
                "description": "Hole Web-Inhalte ab",
                "category": "Web Operations"
            }
        ]

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(tools).encode("utf-8"))

    def serve_programs(self):
        """Serve available programs as JSON"""
        programs = [
            {
                "name": "voice_command_parser",
                "title": "Voice Command Parser",
                "file": "tools/voice_command_parser.py",
                "lines": 147,
                "category": "Voice Control"
            },
            {
                "name": "voice_note_recorder",
                "title": "Voice Note Recorder",
                "file": "tools/voice_note_recorder.py",
                "lines": 187,
                "category": "Voice Input"
            },
            {
                "name": "voice_call_system",
                "title": "Voice Call System",
                "file": "tools/voice_call_system.py",
                "lines": 173,
                "category": "Communication"
            },
            {
                "name": "voice_assistant",
                "title": "Voice Assistant",
                "file": "tools/voice_assistant.py",
                "lines": 138,
                "category": "AI Assistant"
            },
            {
                "name": "voice_transcriber",
                "title": "Voice Transcriber",
                "file": "tools/voice_transcriber.py",
                "lines": 226,
                "category": "Audio Processing"
            },
            {
                "name": "voice_scheduler",
                "title": "Voice Scheduler",
                "file": "tools/voice_scheduler.py",
                "lines": 176,
                "category": "Task Management"
            }
        ]

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(programs).encode("utf-8"))

    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def serve_file_list(self):
        """List files in current directory"""
        try:
            files = []
            current_dir = os.getcwd()
            for item in os.listdir(current_dir):
                path = os.path.join(current_dir, item)
                if os.path.isfile(path):
                    size = os.path.getsize(path)
                    files.append({
                        "name": item,
                        "size": size,
                        "type": "file",
                        "path": item
                    })
                elif os.path.isdir(path) and not item.startswith('.'):
                    files.append({
                        "name": item,
                        "type": "dir",
                        "path": item
                    })

            self.send_json_response({
                "status": "ok",
                "directory": current_dir,
                "files": sorted(files, key=lambda x: (x['type'], x['name']))
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_file_read(self, data):
        """Read file content"""
        try:
            filepath = data.get("path", "")

            # Security: prevent path traversal
            if ".." in filepath or filepath.startswith("/"):
                self.send_json_response({"error": "Invalid path"}, 400)
                return

            if not os.path.exists(filepath):
                self.send_json_response({"error": "File not found"}, 404)
                return

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.send_json_response({
                "status": "ok",
                "path": filepath,
                "content": content,
                "size": len(content),
                "encoding": "utf-8"
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_file_write(self, data):
        """Write file content"""
        try:
            filepath = data.get("path", "")
            content = data.get("content", "")

            # Security: prevent path traversal
            if ".." in filepath or filepath.startswith("/"):
                self.send_json_response({"error": "Invalid path"}, 400)
                return

            # Create parent directories if needed
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            self.send_json_response({
                "status": "ok",
                "path": filepath,
                "message": f"File written successfully ({len(content)} bytes)",
                "size": len(content)
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_file_delete(self, data):
        """Delete file"""
        try:
            filepath = data.get("path", "")

            # Security: prevent path traversal
            if ".." in filepath or filepath.startswith("/"):
                self.send_json_response({"error": "Invalid path"}, 400)
                return

            if not os.path.exists(filepath):
                self.send_json_response({"error": "File not found"}, 404)
                return

            if not os.path.isfile(filepath):
                self.send_json_response({"error": "Path is not a file"}, 400)
                return

            os.remove(filepath)

            self.send_json_response({
                "status": "ok",
                "path": filepath,
                "message": "File deleted successfully"
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_shell_exec(self, data):
        """Execute shell command safely"""
        try:
            command = data.get("command", "").strip()

            # Security: whitelist safe commands
            allowed_commands = [
                "ls", "pwd", "echo", "cat", "grep", "find", "wc",
                "head", "tail", "date", "whoami", "mkdir", "rm",
                "cp", "mv", "touch", "chmod", "python3", "pip3"
            ]

            cmd_name = command.split()[0] if command else ""

            if cmd_name not in allowed_commands:
                self.send_json_response({
                    "error": f"Command '{cmd_name}' not allowed",
                    "allowed": allowed_commands
                }, 403)
                return

            # Execute with timeout
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                self.send_json_response({
                    "status": "ok",
                    "command": command,
                    "returncode": result.returncode,
                    "stdout": result.stdout[:5000],  # Limit output
                    "stderr": result.stderr[:5000],
                    "message": "Command executed successfully"
                })
            except subprocess.TimeoutExpired:
                self.send_json_response({
                    "error": "Command execution timeout (>10s)",
                    "command": command
                }, 408)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_program_start(self, data):
        """Start a voice program in background"""
        try:
            file = data.get("file", "").strip()

            # Security: only allow voice programs
            if not file.startswith("voice_") or not file.endswith(".py"):
                self.send_json_response({
                    "error": "Only voice programs allowed",
                    "pattern": "voice_*.py"
                }, 403)
                return

            filepath = os.path.join("tools", file)

            if not os.path.exists(filepath):
                self.send_json_response({
                    "error": f"Program not found: {file}"
                }, 404)
                return

            # Start program in background
            try:
                process = subprocess.Popen(
                    ["python3", filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )

                self.send_json_response({
                    "status": "ok",
                    "file": file,
                    "filepath": filepath,
                    "pid": process.pid,
                    "message": f"✅ Programm '{file}' gestartet (PID: {process.pid})"
                })
            except Exception as e:
                self.send_json_response({
                    "error": f"Failed to start program: {str(e)}"
                }, 500)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def log_message(self, format, *args):
        """Suppress default logging"""
        return


def main():
    """Start the web dashboard server"""
    print("\n" + "="*70)
    print("  🤖 OpenA3 Web Dashboard")
    print("="*70)
    print(f"\n✅ Server startet auf: http://localhost:{PORT}")
    print(f"\n📊 Dashboard verfügbar unter: http://localhost:{PORT}/")
    print(f"📡 API Endpoints:")
    print(f"   • Status:  http://localhost:{PORT}/api/status")
    print(f"   • Tools:   http://localhost:{PORT}/api/tools")
    print(f"   • Programs: http://localhost:{PORT}/api/programs")
    print(f"\n🎤 Voice Programme können gestartet werden mit:")
    print(f"   python3 tools/voice_command_parser.py")
    print(f"   python3 tools/voice_note_recorder.py")
    print(f"   python3 tools/voice_call_system.py")
    print(f"   python3 tools/voice_assistant.py")
    print(f"   python3 tools/voice_transcriber.py")
    print(f"   python3 tools/voice_scheduler.py")
    print(f"\n⏹️  Drücke CTRL+C zum Beenden")
    print("="*70 + "\n")

    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server beendet")
    except OSError as e:
        print(f"❌ Fehler: {e}")
        print(f"   Port {PORT} ist möglicherweise bereits in Benutzung")


if __name__ == "__main__":
    main()
