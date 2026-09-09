import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN est absent du fichier .env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut !\n\n"
        "PoE Trade Watcher est opérationnel !\n\n"
        "Bientôt, je pourrai surveiller tes recherches PoE."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot démarré...")
    print("📡 En attente de messages Telegram...")

    app.run_polling()


if __name__ == "__main__":
    main()
