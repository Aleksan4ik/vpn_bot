import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import Database

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

SUPPORT_GROUP_ID = -1002345678901

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    
    text = f"""
🔐 Привет, {user.first_name}! 👋

Добро пожаловать в **VPN Bot** - самый надежный VPN сервис!

✨ Что я предлагаю:
• Высокая скорость (до 1 Gbps)
• 30+ серверов по миру
• Полная приватность и шифрование
• 24/7 техподдержка
• Не логируем вашу активность

Выберите действие:
"""
    keyboard = [
        [InlineKeyboardButton("💳 Подписка", callback_data="sub")],
        [InlineKeyboardButton("📞 Поддержка", callback_data="sup")],
        [InlineKeyboardButton("🎁 Бонусы", callback_data="bon")],
        [InlineKeyboardButton("👥 Реферальная", callback_data="ref")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "sub":
        text = """
💳 **ПОДПИСКА НА VPN**

Выберите план:

📅 **1 месяц** - 149₽
📅 **3 месяца** - 399₽
📅 **6 месяцев** - 699₽
📅 **12 месяцев** - 1499₽

Все планы включают:
✅ Все серверы
✅ До 3 устройств
✅ Техподдержка 24/7
"""
        keyboard = [
            [InlineKeyboardButton("1 месяц - 149₽", callback_data="buy_1_149")],
            [InlineKeyboardButton("3 месяца - 399₽", callback_data="buy_3_399")],
            [InlineKeyboardButton("6 месяцев - 699₽", callback_data="buy_6_699")],
            [InlineKeyboardButton("12 месяцев - 1499₽", callback_data="buy_12_1499")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "sup":
        text = """
📞 **СЛУЖБА ПОДДЕРЖКИ**

Напишите ваш вопрос ниже 👇

Наша команда ответит в течение 5 минут!

🔒 Ваше сообщение полностью приватно
✨ Мы не сохраняем ваши данные
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        context.user_data['in_support'] = True
    
    elif query.data == "bon":
        bonuses = db.get_bonuses(user_id)
        text = f"""
🎁 **МОИ БОНУСЫ**

Баланс: **{bonuses} ₽**

Как получить бонусы:
✅ Приглаши друга по реферальной ссылке
✅ Когда друг купит подписку - получи 10% от суммы!

Пример:
• Друг купил за 149₽ → ты получишь 15₽
• Друг купил за 1499₽ → ты получишь 150₽

Бонусы используются как скидка на твою покупку! 💰
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "ref":
        ref_code = db.get_user_ref_code(user_id)
        bonuses = db.get_bonuses(user_id)
        text = f"""
👥 **РЕФЕРАЛЬНАЯ СИСТЕМА**

Твой код: `{ref_code}`

**Как работает:**

1️⃣ Поделись своим кодом с друзьями
2️⃣ Друг вводит твой код при подписке
3️⃣ Ты автоматически получаешь 10% от его покупки!

**Примеры доходов:**
💰 10 друзей × 149₽ = 149₽ бонусов
💰 5 друзей × 1499₽ = 750₽ бонусов

**Твой текущий заработок:** {bonuses}₽

Используй бонусы как скидку на свою подписку! 🚀
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data.startswith("buy_"):
        parts = query.data.split("_")
        plan = f"{parts[1]}_months" if parts[1] != "1" else "1_month"
        price = int(parts[2])
        
        db.create_subscription(user_id, plan, price)
        
        text = f"""
✅ **ПОДПИСКА АКТИВИРОВАНА!**

💳 План: {parts[1]} месяц(ев)
💰 Стоимость: {price}₽
📱 Подключено устройств: 0/3

Твоя подписка активна! 🎉

Команды:
/status - статус подписки
/devices - управление устройствами
/config - получить конфиг

Спасибо за покупку! ❤️
"""
        keyboard = [[InlineKeyboardButton("⬅️ Главное меню", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "back":
        text = "🔐 Главное меню\n\nВыберите действие:"
        keyboard = [
            [InlineKeyboardButton("💳 Подписка", callback_data="sub")],
            [InlineKeyboardButton("📞 Поддержка", callback_data="sup")],
            [InlineKeyboardButton("🎁 Бонусы", callback_data="bon")],
            [InlineKeyboardButton("👥 Реферальная", callback_data="ref")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('in_support'):
        user = update.effective_user
        text = update.message.text
        
        support_msg = f"""
📧 **НОВОЕ СООБЩЕНИЕ В ПОДДЕРЖКУ**

👤 От: {user.first_name} (@{user.username})
🆔 ID: {user.id}

💬 Сообщение:
{text}
"""
        
        try:
            await context.bot.send_message(SUPPORT_GROUP_ID, support_msg, parse_mode='Markdown')
            await update.message.reply_text("✅ Спасибо! Ваше сообщение отправлено. Ответ придет в течение 5 минут.")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await update.message.reply_text("❌ Ошибка. Попробуйте позже.")
        
        context.user_data['in_support'] = False

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🆔 ID этого чата:\n\n`{chat_id}`", parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sub = db.get_active_subscription(user_id)
    
    if sub:
        text = f"""
✅ **СТАТУС ПОДПИСКИ**

💳 План: {sub['plan']}
💰 Цена: {sub['price']}₽
📱 Устройств: {sub['devices_count']}/3
🕐 Действительна до: {sub['end_date']}
"""
    else:
        text = "❌ У вас нет активной подписки.\n\nНажмите /start чтобы купить подписку."
    
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("get_id", get_id))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("✅ Бот включен!")
    app.run_polling()

if __name__ == "__main__":
    main()
