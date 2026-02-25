"""
telegram_bot.py – Telegram-Bot für Ilija Public Edition
Starten: python telegram_bot.py
"""

import os
import asyncio
import logging
import tempfile
import threading
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from kernel import Kernel

load_dotenv()

logging.basicConfig(
    format="%(asctime)s – %(name)s – %(levelname)s – %(message)s",
    level=logging.WARNING
)

TOKEN         = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = set(
    int(uid.strip()) for uid in os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")
    if uid.strip().isdigit()
)

# Globaler Kernel
kernel      = None
kernel_lock = threading.Lock()


def get_kernel() -> Kernel:
    global kernel
    if kernel is None:
        kernel = Kernel()
    return kernel


def is_allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


# ── Command Handlers ──────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(
        "👋 Hallo! Ich bin **Ilija** – dein persönlicher KI-Assistent.\n\n"
        "Ich kann dir helfen mit:\n"
        "📁 Dokumente archivieren und suchen\n"
        "💬 WhatsApp überwachen und beantworten\n"
        "🔍 Internet-Recherchen\n"
        "📅 Termine und Kalender\n\n"
        "Schreib mir einfach, was du brauchst!",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(
        "📖 **Verfügbare Befehle:**\n\n"
        "/start – Begrüßung\n"
        "/help – Diese Hilfe\n"
        "/reload – Skills neu laden\n"
        "/status – System-Status\n"
        "/clear – Chatverlauf löschen\n"
        "/switch – Provider wechseln\n\n"
        "**Für das DMS:**\n"
        "/dms\\_import – Dateien im Import-Ordner anzeigen\n"
        "/dms\\_sort – Dokumente einsortieren\n"
        "/dms\\_stats – Archiv-Statistiken",
        parse_mode="Markdown"
    )


async def cmd_reload(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    with kernel_lock:
        k   = get_kernel()
        msg = k.reload_skills()
    await update.message.reply_text(f"🔄 {msg}")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    with kernel_lock:
        k    = get_kernel()
        info = k.get_debug_info()
    await update.message.reply_text(f"```\n{info}\n```", parse_mode="Markdown")


async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    with kernel_lock:
        k = get_kernel()
        k.state.clear_history()
    await update.message.reply_text("🗑️ Chat-Verlauf gelöscht.")


async def cmd_switch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    args = ctx.args
    mode = args[0].lower() if args else "auto"
    with kernel_lock:
        k   = get_kernel()
        msg = k.switch_provider(mode)
    await update.message.reply_text(msg)


async def cmd_dms_import(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    from skills.dms import dms_import_scan
    result = dms_import_scan()
    await update.message.reply_text(result)


async def cmd_dms_sort(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text("⏳ KI analysiert und sortiert Dokumente ein...")
    with kernel_lock:
        k = get_kernel()
    from skills.dms import dms_einsortieren
    result = dms_einsortieren(provider=k.provider)
    # Lange Nachrichten aufteilen
    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    else:
        await update.message.reply_text(result)


async def cmd_dms_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    from skills.dms import dms_stats, dms_archiv_uebersicht
    stats     = dms_stats()
    uebersicht = dms_archiv_uebersicht()
    msg = (
        f"📊 **DMS-Statistiken**\n\n"
        f"📁 Dokumente gesamt: {stats['gesamt']}\n"
        f"💾 Speicher: {stats['groesse_mb']} MB\n"
        f"📥 Im Import-Ordner: {stats['import_count']}\n\n"
        f"{uebersicht}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


# ── Spracherkennung (synchron für run_in_executor) ────────────
def transcribe_voice_sync(file_path: str) -> str:
    """Spracherkennung via lokalem Whisper oder OpenAI Whisper API."""
    # Variante 1: lokales openai-whisper
    try:
        import whisper, warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="whisper")
        warnings.filterwarnings("ignore", category=UserWarning, module="torch")
        model  = whisper.load_model("base", device="cpu")
        result = model.transcribe(file_path, language="de")
        return result["text"].strip()
    except ImportError:
        pass
    except Exception as e:
        return f"[Whisper Fehler: {e}]"

    # Variante 2: OpenAI Whisper API (falls OPENAI_API_KEY gesetzt)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            with open(file_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=f, language="de"
                )
            return transcript.text.strip()
        except Exception as e:
            return f"[OpenAI Whisper Fehler: {e}]"

    return "[Spracherkennung nicht verfügbar – pip install openai-whisper]"


# ── Message Handler ───────────────────────────────────────────
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    user_input = update.message.text or ""
    if not user_input.strip():
        return

    # Tipp-Indikator
    await ctx.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    with kernel_lock:
        k        = get_kernel()
        response = k.chat(user_input)

    # Lange Antworten aufteilen
    if len(response) > 4000:
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i:i+4000])
    else:
        await update.message.reply_text(response)


async def handle_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Sprachnachrichten transkribieren und an Ilija weiterleiten."""
    if not is_allowed(update.effective_user.id):
        return

    await update.message.reply_text("🎤 Transkribiere Sprachnachricht...")
    voice_file = await ctx.bot.get_file(update.message.voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        await voice_file.download_to_drive(tmp_path)
        loop       = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(None, transcribe_voice_sync, tmp_path)

        if transcript.startswith("["):
            await update.message.reply_text(f"⚠️ {transcript}")
            return

        await update.message.reply_text(f"📝 Erkannt: *{transcript}*", parse_mode="Markdown")
        await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        with kernel_lock:
            k        = get_kernel()
            response = k.chat(transcript)

        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000])
        else:
            await update.message.reply_text(response)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Dokumente direkt in DMS-Import speichern."""
    if not is_allowed(update.effective_user.id):
        return

    doc  = update.message.document
    file = await ctx.bot.get_file(doc.file_id)

    import_dir = os.path.join("data", "dms", "import")
    os.makedirs(import_dir, exist_ok=True)
    filepath = os.path.join(import_dir, doc.file_name)
    await file.download_to_drive(filepath)

    await update.message.reply_text(
        f"📥 **{doc.file_name}** in DMS-Import gespeichert.\n"
        f"Sage 'Dokumente einsortieren' oder nutze /dms\\_sort um sie zu archivieren.",
        parse_mode="Markdown"
    )


async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Fotos (Dokument-Scans) in DMS-Import speichern."""
    if not is_allowed(update.effective_user.id):
        return

    photo    = update.message.photo[-1]  # Größtes Bild
    file     = await ctx.bot.get_file(photo.file_id)
    filename = f"scan_{photo.file_id[:8]}.jpg"

    import_dir = os.path.join("data", "dms", "import")
    os.makedirs(import_dir, exist_ok=True)
    filepath = os.path.join(import_dir, filename)
    await file.download_to_drive(filepath)

    caption = update.message.caption or ""
    if caption:
        prompt = f"Ich habe ein Foto erhalten: {filename}. Beschreibung: {caption}"
    else:
        prompt = f"Ich habe ein Foto/Scan erhalten: {filename}. Es wurde in den DMS-Import-Ordner gespeichert."

    with kernel_lock:
        k        = get_kernel()
        response = k.chat(prompt)

    await update.message.reply_text(
        f"📸 Scan gespeichert als **{filename}**\n\n{response}",
        parse_mode="Markdown"
    )


# ── Bot starten ───────────────────────────────────────────────
def main():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN nicht in .env gesetzt!")
        print("   → Richte einen Bot bei @BotFather ein und trage den Token in .env ein.")
        return

    print(f"\n{'='*50}")
    print(f"  Ilija Public Edition – Telegram Bot")
    print(f"  Erlaubte User-IDs: {ALLOWED_USERS or 'Alle (offen!)'}")
    print(f"{'='*50}\n")

    app_bot = Application.builder().token(TOKEN).build()

    # Commands registrieren
    app_bot.add_handler(CommandHandler("start",      cmd_start))
    app_bot.add_handler(CommandHandler("help",       cmd_help))
    app_bot.add_handler(CommandHandler("reload",     cmd_reload))
    app_bot.add_handler(CommandHandler("status",     cmd_status))
    app_bot.add_handler(CommandHandler("clear",      cmd_clear))
    app_bot.add_handler(CommandHandler("switch",     cmd_switch))
    app_bot.add_handler(CommandHandler("dms_import", cmd_dms_import))
    app_bot.add_handler(CommandHandler("dms_sort",   cmd_dms_sort))
    app_bot.add_handler(CommandHandler("dms_stats",  cmd_dms_stats))

    # Nachrichten-Handler
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.add_handler(MessageHandler(filters.VOICE | filters.AUDIO,   handle_voice))
    app_bot.add_handler(MessageHandler(filters.Document.ALL,            handle_document))
    app_bot.add_handler(MessageHandler(filters.PHOTO,                   handle_photo))

    print("[Ilija] Bot läuft. Schreibe /start in Telegram...")
    app_bot.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
