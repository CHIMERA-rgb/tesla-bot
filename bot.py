import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7210114871:AAENsBqujY6JvVLKT-yu_fK5OlIwNLex05E"
URL = "https://www.tesla.com/tr_tr/modely/design#overview"

# Önceki buton metinlerini saklayacağımız küresel değişken
onceki_butonlar = set()

async def sayfayi_kontrol_et():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            butonlar = soup.find_all("button")
            buton_metinleri = set(b.text.strip() for b in butonlar if b.text.strip())
            return buton_metinleri

async def kontrol_et(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    global onceki_butonlar
    while True:
        try:
            simdiki_butonlar = await sayfayi_kontrol_et()

            if not onceki_butonlar:
                onceki_butonlar = simdiki_butonlar
                print("🔍 İlk butonlar kaydedildi:", simdiki_butonlar)
            elif simdiki_butonlar != onceki_butonlar:
                fark = simdiki_butonlar.symmetric_difference(onceki_butonlar)
                print("🔔 Değişiklik tespit edildi! Fark:", fark)
                onceki_butonlar = simdiki_butonlar
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "🚨 Sayfada değişiklik oldu! Yeni buton(lar):\n\n"
                        + "\n".join(simdiki_butonlar)
                        + "\n\n📍 Sayfayı kontrol et:\n👉 " + URL
                    )
                )
            else:
                print("✅ Değişiklik yok, tekrar denenecek...")

        except Exception as e:
            print("⚠️ Hata oluştu:", e)

        await asyncio.sleep(5)  # Dilediğin aralığı ayarlayabilirsin

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("🔄 Güncellemeler takip ediliyor. Değişiklik olursa haber vereceğim.")
    asyncio.create_task(kontrol_et(context, chat_id))

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🚀 Bot başlatıldı.")
    app.run_polling()

if __name__ == "__main__":
    main()
