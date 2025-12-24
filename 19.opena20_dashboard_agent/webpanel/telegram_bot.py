#!/usr/bin/env python3
"""
Telegram Bot mit Admin-Funktionen
Token: 8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY
"""

import logging
import os
import subprocess
from datetime import datetime
from functools import wraps

import psutil
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TELEGRAM_BOT_TOKEN = "8520488903:AAFwH0XNHk-YPsc_1z1xuqbqrH7BV3Z0tZY"
ADMIN_USER_IDS = []  # Wird beim ersten /start automatisch gesetzt


# Admin-Decorator
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if not ADMIN_USER_IDS:
            ADMIN_USER_IDS.append(user_id)
            logger.info(f"✅ Erster User {user_id} als Admin registriert")

        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ Zugriff verweigert! Nur für Admins.")
            logger.warning(f"⚠️ Unauthorized access by {user_id}")
            return

        return await func(update, context)

    return wrapper


# Basis-Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Hallo {user.mention_html()}!\n\n"
        f"Bot ist online und bereit!\n\n"
        f"📌 Befehle:\n"
        f"/start - Bot starten\n"
        f"/help - Hilfe anzeigen\n"
        f"/info - Bot-Informationen\n"
        f"/admin - Admin-Befehle (nur Admins)"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /help"""
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_USER_IDS or not ADMIN_USER_IDS

    help_text = (
        "📚 Hilfe:\n\n"
        "📌 Basis-Befehle:\n"
        "/start - Bot starten\n"
        "/help - Hilfe anzeigen\n"
        "/info - Bot-Informationen\n\n"
    )

    if is_admin:
        help_text += (
            "🔐 Admin-Befehle:\n"
            "/admin - Admin-Menü\n"
            "/status - System-Status\n"
            "/backup - Backup erstellen\n"
            "/logs - Log-Einträge\n\n"
        )

    help_text += "💬 Sende eine Nachricht und ich antworte!"
    await update.message.reply_text(help_text)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /info"""
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_USER_IDS or not ADMIN_USER_IDS

    await update.message.reply_text(
        "ℹ️ Bot-Informationen:\n\n"
        f"✅ Bot läuft\n"
        f"Chat-ID: {update.effective_chat.id}\n"
        f"User-ID: {user_id}\n"
        f"Admin: {'✅ Ja' if is_admin else '❌ Nein'}\n\n"
        f"Für Admin-Befehle: /admin"
    )


# Admin-Commands
@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /admin"""
    await update.message.reply_text(
        "🔐 Admin-Befehle:\n\n"
        "/status - System-Status (CPU, RAM, Disk)\n"
        "/backup - Backup erstellen\n"
        "/logs - Letzte Log-Einträge\n"
        "/restart - Bot neu starten\n"
        "/addadmin <user_id> - Admin hinzufügen\n"
        "/listadmins - Admins auflisten"
    )


@admin_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /status"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        memory = psutil.virtual_memory()
        ram_total = memory.total / (1024**3)
        ram_used = memory.used / (1024**3)
        ram_percent = memory.percent

        disk = psutil.disk_usage("/")
        disk_total = disk.total / (1024**3)
        disk_used = disk.used / (1024**3)
        disk_percent = disk.percent

        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        status_text = (
            "📊 System-Status:\n\n"
            f"🖥 CPU:\n"
            f"  • Auslastung: {cpu_percent}%\n"
            f"  • Kerne: {cpu_count}\n\n"
            f"💾 RAM:\n"
            f"  • Verwendet: {ram_used:.1f} GB / {ram_total:.1f} GB\n"
            f"  • Auslastung: {ram_percent}%\n\n"
            f"💿 Disk (/):\n"
            f"  • Verwendet: {disk_used:.1f} GB / {disk_total:.1f} GB\n"
            f"  • Auslastung: {disk_percent}%\n\n"
            f"⏱ Uptime: {uptime.days}d {uptime.seconds//3600}h"
        )

        await update.message.reply_text(status_text)

    except Exception as e:
        await update.message.reply_text(f"❌ Fehler: {e}")
        logger.error(f"Status error: {e}")


@admin_only
async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /backup"""
    try:
        await update.message.reply_text("🔄 Erstelle Backup...")

        backup_dir = (
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel/backups"
        )
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.tar.gz"
        backup_path = os.path.join(backup_dir, backup_name)

        source_dir = "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel"

        cmd = [
            "tar",
            "-czf",
            backup_path,
            "-C",
            source_dir,
            "--exclude=backups",
            "--exclude=*.log",
            "--exclude=*.pid",
            "--exclude=__pycache__",
            ".",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            backup_size = os.path.getsize(backup_path) / (1024**2)

            await update.message.reply_text(
                f"✅ Backup erfolgreich!\n\n"
                f"📦 Datei: {backup_name}\n"
                f"📏 Größe: {backup_size:.2f} MB\n"
                f"📂 Pfad: {backup_dir}"
            )
            logger.info(f"Backup created: {backup_path}")
        else:
            await update.message.reply_text(f"❌ Fehler: {result.stderr}")

    except Exception as e:
        await update.message.reply_text(f"❌ Fehler: {e}")
        logger.error(f"Backup error: {e}")


@admin_only
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /logs"""
    try:
        log_file = "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel/telegram_bot.log"

        if not os.path.exists(log_file):
            await update.message.reply_text("❌ Log-Datei nicht gefunden")
            return

        with open(log_file) as f:
            lines = f.readlines()
            last_lines = lines[-20:]
            log_text = "".join(last_lines)

        if len(log_text) > 4000:
            log_text = log_text[-4000:]
            log_text = "...\n" + log_text

        await update.message.reply_text(f"📋 Letzte Logs:\n\n```\n{log_text}\n```", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Fehler: {e}")
        logger.error(f"Logs error: {e}")


@admin_only
async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /restart"""
    await update.message.reply_text("🔄 Bot wird neu gestartet...")
    logger.info("Bot restart requested")

    script_path = "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.opena20_dashboard_agent/webpanel/start_telegram_bot.sh"
    os.execv(script_path, [script_path, "restart"])


@admin_only
async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /addadmin"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /addadmin <user_id>")
        return

    try:
        new_admin_id = int(context.args[0])

        if new_admin_id in ADMIN_USER_IDS:
            await update.message.reply_text(f"ℹ️ User {new_admin_id} ist bereits Admin")
        else:
            ADMIN_USER_IDS.append(new_admin_id)
            await update.message.reply_text(f"✅ User {new_admin_id} wurde als Admin hinzugefügt")
            logger.info(f"New admin: {new_admin_id}")

    except ValueError:
        await update.message.reply_text("❌ Ungültige User-ID")


@admin_only
async def listadmins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler für /listadmins"""
    if not ADMIN_USER_IDS:
        await update.message.reply_text("ℹ️ Keine Admins konfiguriert")
    else:
        admin_list = "\n".join([f"• {admin_id}" for admin_id in ADMIN_USER_IDS])
        await update.message.reply_text(f"👥 Admin User-IDs:\n\n{admin_list}")


# Echo Handler
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo Handler"""
    text = update.message.text
    await update.message.reply_text(f"Du hast geschrieben: {text}")


# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error Handler"""
    logger.error(f"Update {update} caused error {context.error}")


# Main
def main():
    """Startet den Bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Basis-Handler
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))

    # Admin-Handler
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("backup", backup_command))
    application.add_handler(CommandHandler("logs", logs_command))
    application.add_handler(CommandHandler("restart", restart_command))
    application.add_handler(CommandHandler("addadmin", addadmin_command))
    application.add_handler(CommandHandler("listadmins", listadmins_command))

    # Echo (muss am Ende sein)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # Error Handler
    application.add_error_handler(error_handler)

    # Start
    logger.info("🤖 Bot startet mit Admin-Funktionen...")
    logger.info(f"✅ Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    logger.info(f"👥 Admins: {len(ADMIN_USER_IDS) if ADMIN_USER_IDS else 'Keiner (erster User wird Admin)'}")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
