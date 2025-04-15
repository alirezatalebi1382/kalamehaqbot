import json
import logging
import asyncio
import threading
from aiohttp import web # type: ignore
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update  # type: ignore
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)  # type: ignore

#  دیتای چهارده معصوم از فایل data.py
from data import data
#  توکن ربات تلگرام
TOKEN = "7659733690:AAFqmjsngQPqIUg72Bmm8iH5OO6F6s6NMSc"

#  لاگ‌گیری برای دیباگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  aiohttp app برای زنده نگه‌داشتن ربات
async def handle(request):
    return web.Response(text="ربات اسلامی آنلاین است ✅")

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    print("✅ وب سرور aiohttp با موفقیت اجرا شد.")
    await asyncio.Event().wait() # نگه داشتن وب سرور

# ⬇️ دستورات ربات تلگرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in data.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از چهارده معصوم را انتخاب کن:", reply_markup=reply_markup)

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data
    context.user_data["selected"] = name

    keyboard = [[InlineKeyboardButton(key, callback_data=f"info|{key}")] for key in data[name].keys()]
    keyboard.append([InlineKeyboardButton(" بازگشت", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f" {name} - یکی از دسته‌ها را انتخاب کن:", reply_markup=reply_markup)

async def show_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, key = query.data.split("|")
    name = context.user_data.get("selected")
    content = data[name][key]

    # محدودیت تلگرام برای پیام‌های طولانی
    if len(content) > 4000:
        content = content[:3990] + "\n\n[...] ادامه مطلب زیاد است."

    keyboard = [
        [InlineKeyboardButton(" بازگشت", callback_data=name)],
        [InlineKeyboardButton(" بازگشت به منوی اصلی", callback_data="back_to_main")]
    ]
    await query.edit_message_text(f" {key} از {name}:\n\n{content}", reply_markup=InlineKeyboardMarkup(keyboard))

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in data.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(" بازگشت به لیست معصومین:", reply_markup=reply_markup)

# ⏳ تابع اجرای ربات
async def main_bot(app):
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ ربات تلگرام با موفقیت اجرا شد.")
    await asyncio.Event().wait() # نگه داشتن ربات

#  اجرای همزمان aiohttp و Bot
def start_web_server():
    asyncio.run(run_web_server())

def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^(?!info\\||back_to_main).+"))
    app.add_handler(CallbackQueryHandler(show_detail, pattern="^info\\|"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^back_to_main$"))
    asyncio.run(main_bot(app))

if __name__ == "__main__":
    threading.Thread(target=start_web_server).start()
    start_bot()