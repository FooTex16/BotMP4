import logging
import os
import subprocess
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import yt_dlp

# Token bot Anda
BOT_TOKEN = "8188747894:AAHn38-ANrc7lQUfzZYFHmxuXY0jWXxdXh4"

# Setup logging detail
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database tanya jawab custom
QA_DATABASE = {
    "siapa yang buat kamu?": "Saya dibuat oleh developer NiggersCintaAlkautsar.",
    "kenapa kamu dibuat?": "Saya dibuat untuk membantu pengguna melakukan perhitungan, konversi MP4, dan tanya jawab.",
    "dimana kamu belajar?": "Saya belajar dari kode Python dan pengalaman interaksi dengan pengguna.",
    "menggunakan bahasa kamu di program?": "Saya diprogram menggunakan bahasa Python.",
    "menu": "Menu yang bisa kamu coba:\n1. /perhitungan\n2. /convertermp4\n3. /tanyajawab\n4. /fixmp3\n\nKetik /help untuk penjelasan fungsi.",
    "help": (
        "Fungsi dan cara kerja:\n"
        "1. /perhitungan\n"
        "   - Kata penjumlahan: tambah, ditambah, +\n"
        "   - Kata pengurangan: kurang, dikurang, -\n"
        "   - Kata pembagian: bagi, dibagi, /\n"
        "   - Kata perkalian: kali, dikali, x\n"
        "   - Angka: seribu=1000, satu=1, dua=2, dst. Bisa multiple, titik/koma didukung.\n"
        "2. /convertermp4\n"
        "   - Kirim file mp4 ATAU link youtube, lalu bot akan memproses dan mengirim hasil konversi.\n"
        "3. /tanyajawab\n"
        "   - Mulai tanya jawab seputar bot ini.\n"
        "4. /fixmp3\n"
        "   - Kirim file mp3, lalu pilih bitrate 256/320 kbps, bot akan konversi dan kirim hasilnya."
    ),
    "tanya jawab": "Silakan tanya: siapa yang buat kamu?, kenapa kamu dibuat?, dimana kamu belajar?, menggunakan bahasa kamu di program?, dll."
}

# Pesan /start sesuai permintaan
START_MESSAGE = (
    "Selamat Datang Di Bot NiggersCintaAlkautsar\n"
    "Menu yang bisa kamu coba:\n"
    "1. /perhitungan\n"
    "2. /convertermp4\n"
    "3. /tanyajawab\n"
    "4. /fixmp3\n\n"
    "Fungsi dan cara kerja:\n"
    "1. /perhitungan\n"
    "   - Kata untuk penjumlahan: tambah, ditambah, +\n"
    "   - Kata untuk pengurangan: kurang, dikurang, -\n"
    "   - Kata untuk pembagian: bagi, dibagi, /\n"
    "   - Kata untuk perkalian: kali, dikali, x\n"
    "   - 100 ribu, 100k, 100 rb = 100.000\n"
    "   - seribu, 1k, 1 rb = 1.000\n"
    "   - sepuluh ribu, 10k, 10 ribu, 10 rb = 10.000\n"
    "   - 1 juta, 1 jt = 1.000.000\n"
    "   - nol=0, satu=1, dua=2, tiga=3, dst sampai sepuluh=10\n"
    "   - Belasan: sebelas=11, dua belas=12, dst sampai 19\n"
    "   - Puluhan: dua puluh=20, dst. Gabungan: dua puluh satu=21, dst sampai 99\n"
    "   - Bisa multiple, titik/koma didukung (contoh: 1.234 + 32,8 kurang 300)\n\n"
    "2. /convertermp4\n"
    "   - Kirim file mp4 ATAU link youtube yang mau di-convert, bot akan proses dan kirim hasilnya.\n\n"
    "3. /tanyajawab\n"
    "   - Mulai tanya jawab dengan perintah /tanyajawab\n"
    "   - Contoh pertanyaan: siapa yang buat kamu?, kenapa kamu dibuat?, dimana kamu belajar?, menggunakan bahasa kamu di program?, dll.\n\n"
    "4. /fixmp3\n"
    "   - Kirim file mp3, lalu pilih bitrate 256/320 kbps, bot akan konversi dan kirim hasilnya."
)

# State untuk ConversationHandler
(
    CONV_FPS_CHOOSE,
    CONV_YT_LINK,
    CONV_MP3_UPLOAD,
    CONV_MP3_BITRATE,
) = range(4)

# Handler untuk /start
def start(update, context):
    update.message.reply_text(START_MESSAGE)

# Handler untuk /tanyajawab
def tanyajawab(update, context):
    update.message.reply_text(QA_DATABASE["tanya jawab"])

# Handler untuk /perhitungan (dummy, hanya info)
def perhitungan(update, context):
    update.message.reply_text(
        "Silakan ketik perhitunganmu, misal: 1.234 + 32,8 kurang 300\n"
        "Bot akan mencoba membaca dan menghitung sesuai aturan yang dijelaskan di /start."
    )

# Handler untuk /convertermp4
def convertermp4(update, context):
    keyboard = [
        [InlineKeyboardButton("Kirim File MP4", callback_data="mp4_file")],
        [InlineKeyboardButton("Link Youtube", callback_data="yt_link")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Pilih sumber video yang ingin di konversi:\n- Kirim file mp4\n- Atau masukkan link youtube",
        reply_markup=reply_markup
    )
    return CONV_YT_LINK

def convertermp4_callback(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "mp4_file":
        query.edit_message_text("Silakan kirim file mp4 yang ingin di konversi.")
        context.user_data['conv_source'] = 'mp4_file'
        return CONV_FPS_CHOOSE
    elif query.data == "yt_link":
        query.edit_message_text("Silakan masukkan link youtube video yang ingin di konversi.")
        context.user_data['conv_source'] = 'yt_link'
        return CONV_YT_LINK

def handle_yt_link(update, context):
    url = update.message.text.strip()
    context.user_data['yt_url'] = url
    update.message.reply_text(
        "Masukkan FPS yang diinginkan (15-30):\nContoh: 15"
    )
    return CONV_FPS_CHOOSE

def handle_fps_choose(update, context):
    try:
        fps = int(update.message.text.strip())
        if not (15 <= fps <= 30):
            raise ValueError
    except Exception:
        update.message.reply_text("FPS tidak valid! Masukkan angka antara 15 sampai 30.")
        return CONV_FPS_CHOOSE

    context.user_data['fps'] = fps
    source = context.user_data.get('conv_source')
    if source == 'yt_link':
        url = context.user_data.get('yt_url')
        update.message.reply_text("Sedang mendownload video dari Youtube...")
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, 'video.%(ext)s'),
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'merge_output_format': 'mp4',
                'quiet': True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_path = ydl.prepare_filename(info)
                update.message.reply_text("Download selesai. Proses konversi dimulai...")
                output_dir = os.path.join(tmpdir, "Output_MP4")
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_file = f"{base_name} ({fps}fps).avi"
                output_path = os.path.join(output_dir, output_file)
                # Tambahkan hflip ke filter ffmpeg
                vf_filter = "scale=128:160:force_original_aspect_ratio=decrease,pad=128:160:(ow-iw)/2:(oh-ih)/2,hflip"
                cmd = [
                    "ffmpeg", "-y", "-i", video_path,
                    "-vf", vf_filter,
                    "-c:v", "mjpeg", "-q:v", "5", "-b:v", "750k",
                    "-pix_fmt", "yuvj420p", "-r", str(fps),
                    "-c:a", "pcm_s16le", "-ar", "22050",
                    output_path
                ]
                update.message.reply_text(f"Proses konversi: {' '.join(cmd)}")
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    update.message.reply_text(f"Konversi gagal: {result.stderr}")
                    return ConversationHandler.END
                with open(output_path, "rb") as hasil:
                    update.message.reply_document(hasil, filename=output_file, caption="Konversi selesai! Berikut hasil file AVI-nya (dibalik horizontal).")
            except Exception as e:
                update.message.reply_text(f"Terjadi error: {e}")
        return ConversationHandler.END
    elif source == 'mp4_file':
        context.user_data['fps'] = fps
        update.message.reply_text("Silakan kirim file mp4 yang ingin di konversi.")
        return ConversationHandler.END  # File mp4 akan diproses di handler dokumen

# Handler untuk pesan file mp4
def handle_document(update, context):
    document = update.message.document
    if document and document.mime_type == "video/mp4":
        # Tanyakan FPS ke user
        keyboard = [
            [InlineKeyboardButton(str(fps), callback_data=f"fps_{fps}") for fps in range(15, 31, 5)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "File mp4 diterima. Pilih FPS yang diinginkan untuk konversi (15-30):",
            reply_markup=reply_markup
        )
        context.user_data['mp4_file_id'] = document.file_id
        context.user_data['mp4_file_name'] = document.file_name
    else:
        update.message.reply_text("File yang dikirim bukan mp4. Silakan kirim file mp4.")

def handle_fps_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("fps_"):
        fps = int(data.split("_")[1])
        file_id = context.user_data.get('mp4_file_id')
        file_name = context.user_data.get('mp4_file_name', 'video.mp4')
        query.edit_message_text(f"Konversi dimulai dengan FPS {fps}. Mohon tunggu...")
        file = context.bot.get_file(file_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, file_name)
            file.download(input_path)
            output_dir = os.path.join(tmpdir, "Output_MP4")
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(file_name)[0]
            output_file = f"{base_name} ({fps}fps).avi"
            output_path = os.path.join(output_dir, output_file)
            # Tambahkan hflip ke filter ffmpeg
            vf_filter = "scale=128:160:force_original_aspect_ratio=decrease,pad=128:160:(ow-iw)/2:(oh-ih)/2,hflip"
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", vf_filter,
                "-c:v", "mjpeg", "-q:v", "5", "-b:v", "750k",
                "-pix_fmt", "yuvj420p", "-r", str(fps),
                "-c:a", "pcm_s16le", "-ar", "22050",
                output_path
            ]
            context.bot.send_message(chat_id=query.message.chat_id, text=f"Proses konversi: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                context.bot.send_message(chat_id=query.message.chat_id, text=f"Konversi gagal: {result.stderr}")
                return
            with open(output_path, "rb") as hasil:
                context.bot.send_document(chat_id=query.message.chat_id, document=hasil, filename=output_file, caption="Konversi selesai! Berikut hasil file AVI-nya (dibalik horizontal).")

# Handler untuk /fixmp3
def fixmp3(update, context):
    update.message.reply_text("Silakan kirim file mp3 yang ingin di konversi bitrate-nya (256 atau 320 kbps).")
    return CONV_MP3_UPLOAD

def handle_mp3_upload(update, context):
    document = update.message.document
    if document and document.mime_type == "audio/mpeg":
        context.user_data['mp3_file_id'] = document.file_id
        context.user_data['mp3_file_name'] = document.file_name
        keyboard = [
            [InlineKeyboardButton("256 kbps", callback_data="bitrate_256"),
             InlineKeyboardButton("320 kbps", callback_data="bitrate_320")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Pilih bitrate yang diinginkan:", reply_markup=reply_markup)
        return CONV_MP3_BITRATE
    else:
        update.message.reply_text("File yang dikirim bukan mp3. Silakan kirim file mp3.")
        return CONV_MP3_UPLOAD

def handle_bitrate_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("bitrate_"):
        bitrate = int(data.split("_")[1])
        file_id = context.user_data.get('mp3_file_id')
        file_name = context.user_data.get('mp3_file_name', 'audio.mp3')
        query.edit_message_text(f"Konversi dimulai dengan bitrate {bitrate} kbps. Mohon tunggu...")
        file = context.bot.get_file(file_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, file_name)
            file.download(input_path)
            output_file = f"{os.path.splitext(file_name)[0]}_{bitrate}kbps.mp3"
            output_path = os.path.join(tmpdir, output_file)
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:a", f"{bitrate}k",
                output_path
            ]
            context.bot.send_message(chat_id=query.message.chat_id, text=f"Proses konversi: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                context.bot.send_message(chat_id=query.message.chat_id, text=f"Konversi gagal: {result.stderr}")
                return ConversationHandler.END
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            context.bot.send_message(chat_id=query.message.chat_id, text=f"Hasil file: {output_file}\nUkuran: {size_mb:.2f} MB")
            with open(output_path, "rb") as hasil:
                context.bot.send_document(chat_id=query.message.chat_id, document=hasil, filename=output_file, caption=f"Konversi selesai ke {bitrate} kbps.")
        return ConversationHandler.END

# Handler untuk pesan tanya jawab
def handle_message(update, context):
    text = update.message.text.lower()
    user_name = update.effective_user.full_name if update.effective_user else "User"
    logger.info(f"Pesan dari [{user_name}]: {text}")

    # Cek database tanya jawab
    response = None
    for question, answer in QA_DATABASE.items():
        if text == question.lower():
            response = answer
            break

    if not response:
        response = "Maaf, saya belum bisa menjawab pertanyaan tersebut. Silakan gunakan /menu atau /help untuk melihat fitur."

    update.message.reply_text(response)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", handle_message))
    dp.add_handler(CommandHandler("help", handle_message))
    dp.add_handler(CommandHandler("tanyajawab", tanyajawab))
    dp.add_handler(CommandHandler("perhitungan", perhitungan))

    # Handler untuk convertermp4 (Conversation)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("convertermp4", convertermp4)],
        states={
            CONV_YT_LINK: [
                CallbackQueryHandler(convertermp4_callback),
                MessageHandler(Filters.text & ~Filters.command, handle_yt_link)
            ],
            CONV_FPS_CHOOSE: [
                MessageHandler(Filters.text & ~Filters.command, handle_fps_choose)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)

    # Handler untuk file mp4 (memicu pemilihan FPS)
    dp.add_handler(MessageHandler(Filters.document.video, handle_document))
    dp.add_handler(CallbackQueryHandler(handle_fps_callback, pattern=r"^fps_\d+$"))

    # Handler untuk fixmp3 (Conversation)
    fixmp3_handler = ConversationHandler(
        entry_points=[CommandHandler("fixmp3", fixmp3)],
        states={
            CONV_MP3_UPLOAD: [
                MessageHandler(Filters.document.audio, handle_mp3_upload)
            ],
            CONV_MP3_BITRATE: [
                CallbackQueryHandler(handle_bitrate_callback, pattern=r"^bitrate_\d+$")
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )
    dp.add_handler(fixmp3_handler)

    # Handler pesan tanya jawab
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logger.info("Bot siap dijalankan...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
