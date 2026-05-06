import logging
import re
import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8497889306:AAGopPlx_NoU0x6ru6o8qa6RnULy_LOOV0I"

URL_PATTERN = r"https?://[^\s]+"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def extract_url(text):
    match = re.search(URL_PATTERN, text)
    return match.group(0) if match else None

def download(url):
    output = "downloaded_video"

    for e in ["mp4", "mkv", "webm"]:
        p = f"{output}.{e}"
        if os.path.exists(p):
            os.remove(p)

    opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output + ".%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "http_headers": HEADERS,
        "merge_output_format": "mp4",
        # Chrome brauzeridan avtomatik cookies oladi
        "cookiesfrombrowser": ("chrome",),
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)

    for e in ["mp4", "mkv", "webm"]:
        p = f"{output}.{e}"
        if os.path.exists(p):
            return p
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n"
        "YouTube, Instagram, TikTok havolasini yuboring!\n\n"
        "أهلاً! أرسل رابط YouTube أو Instagram أو TikTok!"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    url = extract_url(text)

    if not url:
        await update.message.reply_text("❌ Havola topilmadi!")
        return

    msg = await update.message.reply_text("⏳ Yuklab olinmoqda...")

    try:
        path = download(url)

        if not path:
            await msg.edit_text("❌ Video yuklab olinmadi.")
            return

        if os.path.getsize(path) > 50 * 1024 * 1024:
            os.remove(path)
            await msg.edit_text("⚠️ Video juda katta (50MB+).")
            return

        await msg.edit_text("📤 Yuborilmoqda...")
        with open(path, "rb") as f:
            await update.message.reply_video(video=f, caption="✅ Mana!")
        os.remove(path)
        await msg.delete()

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await msg.edit_text(f"❌ Xatolik: {str(e)[:300]}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    logger.info("🤖 Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
