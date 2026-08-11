import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔐 Привет! Добро пожаловать в VPN Bot!\n\nВыберите действие:"
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
        text = "💳 Подписка\n\n1 месяц - 149₽\n3 месяца - 399₽\n6 месяцев - 699₽\n12 месяцев - 1499₽"
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    elif query.data == "sup":
        text = "📞 Служба поддержки 24/7"
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    elif query.data == "bon":
        text = "🎁 У вас 0₽ бонусов"
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    elif query.data == "ref":
        text = "👥 Реферальная система\n\nТвой код: VPN123ABC\n\nПриглашай друзей и получай 10% от их покупки!"
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    elif query.data == "back":
        text = "🔐 Главное меню\n\nВыберите действие:"
        keyboard = [
            [InlineKeyboardButton("💳 Подписка", callback_data="sub")],
            [InlineKeyboardButton("📞 Поддержка", callback_data="sup")],
            [InlineKeyboardButton("🎁 Бонусы", callback_data="bon")],
            [InlineKeyboardButton("👥 Реферальная", callback_data="ref")]
        ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Бот включен!")
    app.run_polling()

if __name__ == "__main__":
    main()
