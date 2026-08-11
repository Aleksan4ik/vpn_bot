import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔐 Привет! Выберите действие:"
    keyboard = [
        [InlineKeyboardButton("💳 Подписка", callback_data="sub")],
        [InlineKeyboardButton("📞 Поддержка", callback_data="sup")],
        [InlineKeyboardButton("🎁 Бонусы", callback_data="bon")],
        [InlineKeyboardButton("👥 Реферальная", callback_data="ref")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "sub":
        await query.edit_message_text("💳 Подписка:\n1м - 149₽\n3м - 399₽\n6м - 699₽\n12м - 1499₽")
    elif query.data == "sup":
        await query.edit_message_text("📞 Напишите вопрос")
    elif query.data == "bon":
        await query.edit_message_text("🎁 Бонусы: 0₽")
    elif query.data == "ref":
        await query.edit_message_text("👥 Код: VPN123\nПриглашай друзей!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Бот включен!")
    app.run_polling()

if __name__ == "__main__":
    main()
