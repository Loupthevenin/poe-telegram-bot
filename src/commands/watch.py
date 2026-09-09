import re
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import ContextTypes

from src.database import (
    create_watch,
    delete_watch,
    get_user_watches,
)


TRADE_HOST = "www.pathofexile.com"

TRADE_PATH_PATTERN = re.compile(r"^/trade/search/([^/]+)/([^/?#]+)/live$")


def parse_trade_url(url: str) -> tuple[str, str] | None:
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return None

        if parsed.netloc.lower() != TRADE_HOST:
            return None

        match = TRADE_PATH_PATTERN.match(parsed.path)

        if not match:
            return None

        league = match.group(1)
        query_id = match.group(2)

        if not league or not query_id:
            return None

        return league, query_id

    except ValueError:
        return None


async def watch_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Il manque l'URL.\n\n"
            "Utilisation :\n"
            "/watch https://www.pathofexile.com/trade/search/League/QUERY_ID"
        )
        return

    url = context.args[0].strip()

    parsed = parse_trade_url(url)

    if parsed is None:
        await update.message.reply_text(
            "❌ URL Trade PoE invalide.\n\n"
            "Exemple :\n"
            "https://www.pathofexile.com/trade/search/League/QUERY_ID"
        )
        return

    league, query_id = parsed

    watch = create_watch(
        telegram_user_id=update.effective_user.id,
        league=league,
        query_id=query_id,
        url=url,
    )

    await update.message.reply_text(
        "✅ Surveillance créée !\n\n"
        f"🆔 #{watch.id}\n"
        f"🌐 League : {watch.league}\n"
        f"🔎 Recherche : {watch.query_id}\n"
        "📡 Statut : En attente du Live Search"
    )


async def watches_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    watches = get_user_watches(update.effective_user.id)

    if not watches:
        await update.message.reply_text("📭 Tu n'as aucune surveillance active.")
        return

    lines = ["🔔 Tes surveillances\n"]

    for watch in watches:
        status = {
            "pending": "🟡",
            "active": "🟢",
            "paused": "⏸️",
            "error": "🔴",
        }.get(watch.status, "⚪")

        lines.append(
            f"{status} #{watch.id} — {watch.league}\n"
            f"   🔎 {watch.query_id}\n"
            f"   📡 {watch.status}"
        )

    await update.message.reply_text("\n\n".join(lines))


async def unwatch_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Indique l'identifiant de la surveillance.\n\n"
            "Exemple :\n"
            "/unwatch 1"
        )
        return

    try:
        watch_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ L'identifiant doit être un nombre.")
        return

    deleted = delete_watch(
        watch_id=watch_id,
        telegram_user_id=update.effective_user.id,
    )

    if not deleted:
        await update.message.reply_text(f"❌ La surveillance #{watch_id} n'existe pas.")
        return

    await update.message.reply_text(f"🗑️ Surveillance #{watch_id} supprimée.")
