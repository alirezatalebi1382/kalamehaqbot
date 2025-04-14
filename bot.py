import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update  # type: ignore
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes  # type: ignore

# فعال‌سازی لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اطلاعات چهارده معصوم
from data import data
# زندگی نامه اهل بیت
# دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in data.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از چهارده معصوم را انتخاب کن:", reply_markup=reply_markup)

# نمایش دسته‌بندی برای هر معصوم
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data
    context.user_data["selected"] = name

    keyboard = [[InlineKeyboardButton(key, callback_data=f"info|{key}")] for key in data[name].keys()]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🔍 {name} - یکی از دسته‌ها را انتخاب کن:", reply_markup=reply_markup)

# نمایش اطلاعات هر دسته
async def show_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, key = query.data.split("|")
    name = context.user_data.get("selected")
    content = data[name][key]
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data=name)],
        [InlineKeyboardButton("🔝 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ]
    
    # جلوگیری از طولانی بودن پیام
    if len(content) > 4000:
        content = content[:3990] + "\n\n[...] 🔽 ادامه مطلب زیاد است."
    
    await query.edit_message_text(f"📌 {key} از {name}:\n\n{content}", reply_markup=InlineKeyboardMarkup(keyboard))

# بازگشت به لیست معصومین
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in data.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔙 بازگشت به لیست معصومین:", reply_markup=reply_markup)

# راه‌اندازی ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token("7659733690:AAHearEE5h2kRHXcX8s-ccgYVjNXg8zRCjA").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^(?!info\\||back_to_main).+"))
    app.add_handler(CallbackQueryHandler(show_detail, pattern="^info\\|"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^back_to_main$"))

    print("✅ ربات شما با موفقیت اجرا شد.")
    app.run_polling()
