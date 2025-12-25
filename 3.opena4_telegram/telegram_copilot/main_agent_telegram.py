import os

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "DEIN_TOKEN_HIER")


def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Willkommen beim Telegram CoPilot!")


def handle_text(update: Update, context: CallbackContext):
    user_input = update.message.text
    response = f"🤖 Echo: {user_input}"
    update.message.reply_text(response)


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
