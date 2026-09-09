import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from src.commands.watch import (
    unwatch_command,
    watch_command,
    watches_command,
)
from src.database import init_database


load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN est absent du fichier .env")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "👋 Salut !\n\n"
        "PoE Trade Watcher est opérationnel.\n\n"
        "Commandes disponibles :\n"
        "/watch <URL> — surveiller une recherche\n"
        "/watches — afficher tes surveillances\n"
        "/unwatch <ID> — supprimer une surveillance"
    )


def main() -> None:
    init_database()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("watch", watch_command))

    application.add_handler(CommandHandler("watches", watches_command))

    application.add_handler(CommandHandler("unwatch", unwatch_command))

    logger.info("Bot démarré")

    application.run_polling()


if __name__ == "__main__":
    main()
