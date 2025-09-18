import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========================
# Masukkan token bot kamu
# ========================
BOT_TOKEN = "8188747894:AAHn38-ANrc7lQUfzZYFHmxuXY0jWXxdXh4"

# Aktifkan logging (debugging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Halo {user.first_name}! 👋\nBot Telegram kamu sudah aktif di Render 🚀")

# Handler untuk semua pesan teks (echo)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_received = update.message.text
    await update.message.reply_text(f"Kamu mengirim: {text_received}")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Tambahkan command handler
    app.add_handler(CommandHandler("start", start))

    # Tambahkan handler untuk semua pesan teks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Jalankan bot
    logger.info("Bot sedang berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
