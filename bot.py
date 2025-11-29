import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение переменных окружения
BOT_TOKEN = os.getenv('8564008392:AAEdPESAcK8pcBPR359q2gopR9DMh1r1hXs')
ADMIN_CHAT_ID = os.getenv('7288679331')

print("=" * 50)
print("🚀 ЗАПУСК БОТА")
print(f"BOT_TOKEN: {'✅ Установлен' if BOT_TOKEN else '❌ НЕ установлен'}")
print(f"ADMIN_CHAT_ID: {'✅ Установлен' if ADMIN_CHAT_ID else '❌ НЕ установлен'}")
print("=" * 50)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🌐 Сайты", callback_data="sites")],
        [InlineKeyboardButton("🤖 Боты", callback_data="bots")],
        [InlineKeyboardButton("🎨 Веб-дизайн", callback_data="web_design")],
        [InlineKeyboardButton("📁 Прочее", callback_data="other")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ Выберите тип проекта:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['project_type'] = query.data
    await query.edit_message_text("📝 Опишите ваш проект подробно:")
    context.user_data['waiting_for_description'] = True

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_for_description'):
        context.user_data['project_description'] = update.message.text
        keyboard = [[InlineKeyboardButton("🚀 Отправить заказ", callback_data="send_order")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ Описание получено!", reply_markup=reply_markup)
        context.user_data['waiting_for_description'] = False

async def send_order_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    project_type = context.user_data.get('project_type', 'Не указан')
    project_description = context.user_data.get('project_description', 'Не указано')
    
    order_message = f"""
🎉 НОВЫЙ ЗАКАЗ!

Заказчик: {user.first_name} (@{user.username})
Тип: {project_type}
Описание: {project_description}
"""
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_message)
        await query.edit_message_text("🎊 Заказ отправлен! Мы свяжемся с вами.")
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(sites|bots|web_design|other)$"))
    application.add_handler(CallbackQueryHandler(send_order_to_admin, pattern="^send_order$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))
    
    print("🤖 Бот запущен и работает!")
    application.run_polling()

if __name__ == "__main__":
    main()
