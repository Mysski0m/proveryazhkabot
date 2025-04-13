from functions import (start, target_menu, support_menu, main_menu, send_test,
                       test_answer, contact, forward_message_to_or_for_teacher,
                       get_bank)
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import json

with open("info.json", encoding="UTF-8") as file_in:
    data = json.load(file_in)

MY_CHAT_ID = data["ADMIN_ID"]
TOKEN = data["TOKEN"]

def start_message(update: Update, context: CallbackContext):
    update.message.reply_text("Привет!")

def notify_admin(bot: Bot):
    bot.send_message(chat_id=MY_CHAT_ID, text="🤖 Бот запущен и готов к работе!")

# Основная функция
def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start_message", start_message))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex('^(Цели)$'), target_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Банк)$'), get_bank))
    dp.add_handler(MessageHandler(Filters.regex('^(Главное меню)$'), main_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Отправить работу)$'), contact))
    dp.add_handler(MessageHandler(Filters.regex('^(Поддержка)$'), support_menu))


    # # Добавляем фильтры для кнопок ОГЭ
    # for i in range(1, 13):
    #     dp.add_handler(MessageHandler(Filters.regex(f'^№{i}$'), send_test))

    # # Добавляем фильтры для кнопок ЕГЭ
    # for i in range(1, 28):
    #     dp.add_handler(MessageHandler(Filters.regex(f'^№{i}$'), send_test))

    dp.add_handler(CallbackQueryHandler(test_answer))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message_to_or_for_teacher))
    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, forward_message_to_or_for_teacher))

    updater.start_polling()
    notify_admin(updater.bot)
    updater.idle()


if __name__ == "__main__":
    main()
