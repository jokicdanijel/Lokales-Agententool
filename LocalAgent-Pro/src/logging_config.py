#!/usr/bin/env python3
"""
LocalAgent-Pro Logging-Konfiguration
Umfassendes Logging für Backend und Ollama-Integration
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

# =================
# LOGGING CONFIG
# =================

class ColoredFormatter(logging.Formatter):
    """Formatter mit Farben für Console-Ausgabe"""
    
    # ANSI-Farbcodes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Grün
        'WARNING': '\033[33m',   # Gelb
        'ERROR': '\033[31m',     # Rot
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Fügt Farben zum Log-Record hinzu"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname_colored = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Original levelname für File-Logging bewahren
        original_levelname = record.levelname
        record.levelname = record.levelname_colored
        
        formatted = super().format(record)
        
        # Levelname zurücksetzen
        record.levelname = original_levelname
        
        return formatted


class LoggingManager:
    """Zentrale Logging-Verwaltung für LocalAgent-Pro"""
    
    def __init__(
        self, 
        app_name: str = "LocalAgent-Pro",
        log_dir: Optional[str] = None,
        log_level: str = "DEBUG",
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        console_output: bool = True
    ):
        """
        Initialisiert Logging-Manager
        
        Args:
            app_name: Name der Applikation
            log_dir: Verzeichnis für Log-Dateien (None = ./logs)
            log_level: Standard-Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_file_size: Max. Größe pro Log-Datei in Bytes
            backup_count: Anzahl rotierter Backup-Dateien
            console_output: Logs auch in Konsole ausgeben
        """
        self.app_name = app_name
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_output = console_output
        
        # Log-Verzeichnis
        if log_dir is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            log_dir = os.path.join(base_dir, "logs")
        
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Logger initialisieren
        self.loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Konfiguriert Root-Logger"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Vorhandene Handler entfernen
        root_logger.handlers.clear()
        
        # File Handler mit Rotation
        log_file = os.path.join(self.log_dir, f"{self.app_name.lower()}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # File Formatter (ohne Farben)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console Handler (mit Farben)
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            console_formatter = ColoredFormatter(
                '%(asctime)s | %(levelname_colored)s | %(name)-15s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Spezielle Handler für Drittanbieter-Bibliotheken
        self._configure_third_party_loggers()
        
        root_logger.info("=" * 80)
        root_logger.info(f"🚀 {self.app_name} Logging initialisiert")
        root_logger.info(f"📁 Log-Verzeichnis: {self.log_dir}")
        root_logger.info(f"📊 Log-Level: {logging.getLevelName(self.log_level)}")
        root_logger.info(f"💾 Max. Dateigröße: {self.max_file_size / 1024 / 1024:.1f} MB")
        root_logger.info(f"🔄 Backup-Anzahl: {self.backup_count}")
        root_logger.info("=" * 80)
    
    def _configure_third_party_loggers(self):
        """Konfiguriert Logging für Drittanbieter-Bibliotheken"""
        # Werkzeug (Flask) auf INFO setzen
        logging.getLogger('werkzeug').setLevel(logging.INFO)
        
        # urllib3 (requests) auf WARNING setzen (zu verbose auf DEBUG)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # requests auf INFO
        logging.getLogger('requests').setLevel(logging.INFO)
        
        # Flask auf INFO
        logging.getLogger('flask').setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Erstellt oder holt einen Logger mit dem angegebenen Namen
        
        Args:
            name: Logger-Name (z.B. "API", "Tools", "Ollama")
        
        Returns:
            Konfigurierter Logger
        """
        if name not in self.loggers:
            logger = logging.getLogger(f"{self.app_name}.{name}")
            logger.setLevel(self.log_level)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def create_request_logger(self) -> logging.Logger:
        """Erstellt speziellen Logger für API-Requests"""
        logger = self.get_logger("API-Requests")
        
        # Zusätzlicher File Handler für API-Requests
        api_log_file = os.path.join(self.log_dir, "api_requests.log")
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        api_formatter = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_handler.setFormatter(api_formatter)
        logger.addHandler(api_handler)
        
        return logger
    
    def create_ollama_logger(self) -> logging.Logger:
        """Erstellt speziellen Logger für Ollama-Integration"""
        logger = self.get_logger("Ollama")
        
        # Zusätzlicher File Handler für Ollama
        ollama_log_file = os.path.join(self.log_dir, "ollama_integration.log")
        ollama_handler = logging.handlers.RotatingFileHandler(
            ollama_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        ollama_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ollama_handler.setFormatter(ollama_formatter)
        logger.addHandler(ollama_handler)
        
        return logger
    
    def create_tool_logger(self) -> logging.Logger:
        """Erstellt speziellen Logger für Tool-Ausführungen"""
        logger = self.get_logger("Tools")
        
        # Zusätzlicher File Handler für Tools
        tool_log_file = os.path.join(self.log_dir, "tool_executions.log")
        tool_handler = logging.handlers.RotatingFileHandler(
            tool_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        tool_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        tool_handler.setFormatter(tool_formatter)
        logger.addHandler(tool_handler)
        
        return logger
    
    def log_request(self, endpoint: str, method: str, data: dict, response_status: int):
        """
        Loggt einen vollständigen API-Request
        
        Args:
            endpoint: API-Endpunkt
            method: HTTP-Methode
            data: Request-Daten
            response_status: HTTP-Status-Code
        """
        logger = self.get_logger("API")
        logger.info(
            f"📨 {method} {endpoint} | Status: {response_status} | "
            f"Data Size: {len(str(data))} bytes"
        )
        logger.debug(f"📦 Request Data: {data}")
    
    def set_log_level(self, level: str):
        """
        Ändert Log-Level zur Laufzeit
        
        Args:
            level: Neuer Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper(), logging.DEBUG)
        self.log_level = new_level
        
        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(new_level)
        
        root_logger.info(f"🔧 Log-Level geändert auf: {level.upper()}")


# =================
# UTILITY FUNCTIONS
# =================

def mask_sensitive_data(text: str, patterns: list = None) -> str:
    """
    Maskiert sensible Daten in Logs
    
    Args:
        text: Zu maskierender Text
        patterns: Liste von Regex-Patterns für sensible Daten
    
    Returns:
        Maskierter Text
    """
    import re
    
    if patterns is None:
        # Standard-Patterns für sensible Daten
        patterns = [
            (r'password["\s:=]+([^"\s,]+)', 'password: ***MASKED***'),
            (r'api[_-]?key["\s:=]+([^"\s,]+)', 'api_key: ***MASKED***'),
            (r'token["\s:=]+([^"\s,]+)', 'token: ***MASKED***'),
            (r'secret["\s:=]+([^"\s,]+)', 'secret: ***MASKED***'),
        ]
    
    masked_text = text
    for pattern, replacement in patterns:
        masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
    
    return masked_text


def truncate_long_content(content: str, max_length: int = 1000) -> str:
    """
    Kürzt langen Content für Logging
    
    Args:
        content: Zu kürzender Inhalt
        max_length: Maximale Länge
    
    Returns:
        Gekürzter Inhalt
    """
    if len(content) <= max_length:
        return content
    
    return f"{content[:max_length]}... (gekürzt, Original: {len(content)} Zeichen)"


# =================
# GLOBAL INSTANCE
# =================

# Globale Logging-Manager-Instanz (kann importiert werden)
_global_logging_manager = None

def get_logging_manager(**kwargs) -> LoggingManager:
    """
    Holt oder erstellt globale LoggingManager-Instanz
    
    Returns:
        LoggingManager-Instanz
    """
    global _global_logging_manager
    
    if _global_logging_manager is None:
        _global_logging_manager = LoggingManager(**kwargs)
    
    return _global_logging_manager


# =================
# EXAMPLE USAGE
# =================

if __name__ == "__main__":
    # Beispiel-Nutzung
    manager = get_logging_manager(
        app_name="LocalAgent-Pro",
        log_level="DEBUG",
        console_output=True
    )
    
    # Logger erstellen
    api_logger = manager.get_logger("API")
    tool_logger = manager.create_tool_logger()
    ollama_logger = manager.create_ollama_logger()
    
    # Test-Logs
    api_logger.debug("Debug-Message für API")
    api_logger.info("Info-Message für API")
    api_logger.warning("Warning-Message für API")
    api_logger.error("Error-Message für API")
    
    tool_logger.info("Tool 'read_file' wurde aufgerufen")
    ollama_logger.info("Verbindung zu Ollama erfolgreich")
    
    # Sensible Daten maskieren
    sensitive = "password: secret123, api_key: abc-def-ghi"
    masked = mask_sensitive_data(sensitive)
    api_logger.info(f"Masked: {masked}")
    
    print("\n✅ Logging-Test abgeschlossen. Prüfe logs/ Verzeichnis!")
