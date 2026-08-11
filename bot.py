import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    if user_id not in users_data:
        users_data[user_id] = {
            'name': first_name,
            'ref_code': f'VPN{user_id}',
            'bonuses': 0,
            'subscription': None
        }
    
    text = f"""
🔐 Привет, {first_name}! 👋

Добро пожаловать в **VPN Bot**!

✨ Лучший VPN сервис:
• Скорость до 1 Gbps
• 30+ серверов
• Полная приватность
• Поддержка 24/7

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

Все планы:
✅ Все серверы
✅ До 3 устройств
✅ Поддержка 24/7
"""
        keyboard = [
            [InlineKeyboardButton("Купить 1 месяц - 149₽", callback_data="buy_1_149")],
            [InlineKeyboardButton("Купить 3 месяца - 399₽", callback_data="buy_3_399")],
            [InlineKeyboardButton("Купить 6 месяцев - 699₽", callback_data="buy_6_699")],
            [InlineKeyboardButton("Купить 12 месяцев - 1499₽", callback_data="buy_12_1499")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "sup":
        text = """
📞 **СЛУЖБА ПОДДЕРЖКИ**

Напишите ваш вопрос ниже! 👇

Ответим в течение 5 минут!

🔒 Приватно
✨ Анонимно
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        context.user_data['support_mode'] = True
    
    elif query.data == "bon":
        bonuses = users_data[user_id]['bonuses']
        text = f"""
🎁 **МОИ БОНУСЫ**

Баланс: **{bonuses} ₽**

Как получить:
✅ Приглаши друга
✅ Друг купит подписку
✅ Получи 10% от его покупки!

Пример:
• Друг купил 149₽ → ты +15₽
• Друг купил 1499₽ → ты +150₽

Бонусы - это скидка на твою подписку! 💰
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "ref":
        ref_code = users_data[user_id]['ref_code']
        bonuses = users_data[user_id]['bonuses']
        text = f"""
👥 **РЕФЕРАЛЬНАЯ СИСТЕМА**

Твой код: `{ref_code}`

**Как работает:**
1️⃣ Поделись кодом с друзьями
2️⃣ Друг купит подписку
3️⃣ Ты получи 10% от его покупки!

**Твой заработок:** {bonuses}₽

Начни приглашать! 🚀
"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data.startswith("buy_"):
        plan_info = query.data.split("_")
        plan = plan_info[1]
        price = int(plan_info[2])
        
        if user_id not in users_data:
            users_data[user_id] = {'name': 'User', 'ref_code': f'VPN{user_id}', 'bonuses': 0, 'subscription': None}
        
        users_data[user_id]['subscription'] = {'plan': plan, 'price': price}
        
        text = f"""
✅ **ПОДПИСКА АКТИВИРОВАНА!**

💳 План: {plan} месяц(ев)
💰 Цена: {price}₽
📱 Устройств: 0/3

Спасибо за покупку! ❤️

Команды:
/status - статус подписки
/start - главное меню
"""
        keyboard = [[InlineKeyboardButton("⬅️ Главное меню", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif query.data == "back":
        text = "🔐 **Главное меню**\n\nВыберите действие:"
        keyboard = [
            [InlineKeyboardButton("💳 Подписка", callback_data="sub")],
            [InlineKeyboardButton("📞 Поддержка", callback_data="sup")],
            [InlineKeyboardButton("🎁 Бонусы", callback_data="bon")],
            [InlineKeyboardButton("👥 Реферальная", callback_data="ref")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('support_mode'):
        text = update.message.text
        await update.message.reply_text("✅ Спасибо! Сообщение отправлено. Ответим в течение 5 минут.")
        context.user_data['support_mode'] = False

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in users_data and users_data[user_id].get('subscription'):
        sub = users_data[user_id]['subscription']
        text = f"""
✅ **СТАТУС ПОДПИСКИ**

💳 План: {sub['plan']} месяц(ев)
💰 Цена: {sub['price']}₽
📱 Устройств: 0/3
"""
    else:
        text = "❌ У вас нет активной подписки.\n\nНажмите /start чтобы купить."
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("✅ Бот включен!")
    app.run_polling()

if __name__ == "__main__":
    main()
