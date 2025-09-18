import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ======================
# TOKEN BOT
# ======================
BOT_TOKEN = "8188747894:AAHn38-ANrc7lQUfzZYFHmxuXY0jWXxdXh4"

# ======================
# Logging
# ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======================
# Handler Commands
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Bot sudah aktif ✅\n\nCoba kirim pesan teks apa saja."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Kamu kirim: {text}")

# ======================
# Main Function
# ======================
def main():
    # Pakai Application (PTB v20+)
    application = Application.builder().token(BOT_TOKEN).build()

    # Handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Bot berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
