from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from questions import ege_questions, oge_questions
from main import MY_CHAT_ID

# MY_CHAT_ID =   # ID пользователя, которому будет отправляться сообщение

List_Of_Students_Answers = {}

List_Of_Students_Statistics = {}

# User_Bank = 0

# Стартовое меню
def start(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его.")
    #     return
    if update.message.chat_id not in List_Of_Students_Statistics:
        List_Of_Students_Statistics[update.message.chat_id] = 0
    keyboard = [
        ['Цели', 'Банк'],
        ['Отправить работу'],
        ['Поддержка']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

# Обработчик для целей
def target_menu(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его.")
    #     return

    context.user_data['current_menu'] = "Цели"
    context.user_data['awaiting_contact_message'] = False
    keyboard = [
        ["Главное меню"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Цели:', reply_markup=reply_markup)
    update.message.reply_text('Вот список текущих целей:\n бебра\n бебра', reply_markup=reply_markup)

# Обработчик для поддержки
def support_menu(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его")
    #     return

    context.user_data['current_menu'] = "Поддержка"
    context.user_data['awaiting_contact_message'] = False
    keyboard = [
        ['Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Поддержка:', reply_markup=reply_markup)

# Возвращение в главное меню
def main_menu(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его")
    #     return

    context.user_data['awaiting_contact_message'] = False
    start(update, context)

# Функция отправки тестового задания
def send_test(update: Update, context: CallbackContext) -> None:
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его.")
    #     return

    current_menu = context.user_data.get('current_menu')
    if not current_menu:
        update.message.reply_text('Пожалуйста, выберите категорию: ОГЭ или ЕГЭ')
        return

    questions = oge_questions if current_menu == 'ОГЭ' else ege_questions

    try:
        task_number = int(update.message.text.replace("№", ""))
    except ValueError:
        update.message.reply_text("Введите корректный номер задания.")
        return

    test_set = questions.get(task_number)
    if not test_set:
        update.message.reply_text("Некорректный номер задания.")
        return

    context.user_data['test_set'] = test_set
    context.user_data['test_question'] = None
    context.user_data['selected_options'] = set()

    if test_set["type"] == "input_task":
        context.user_data['input_question_active'] = True
        context.user_data['input_question'] = test_set
        context.bot.send_message(chat_id=update.effective_chat.id, text=test_set["question"], parse_mode='Markdown')

    elif test_set["type"] == "multichoice_task":
        keyboard = [[InlineKeyboardButton("➖ " + opt, callback_data=f"{i}:False")] for i, opt in enumerate(test_set ['options'])]
        keyboard.append([InlineKeyboardButton("Проверить ответы", callback_data="submit")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["multichoice_question_active"] = True
        context.user_data["multichoice_question"] = test_set
        context.bot.send_message(chat_id=update.effective_chat.id, text=test_set["question"], reply_markup=reply_markup, parse_mode='Markdown')

    elif test_set["type"] == "text_task":
        context.user_data['text_question_active'] = True
        context.user_data['text_question'] = test_set
        if 'image' in test_set:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=test_set['image'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=test_set["question"], parse_mode='Markdown')

    else:
        update.message.reply_text("Произошла ошибка, попробуйте ещё раз.")

# Обработчик команды проверки ввода
def check_input(update: Update, context: CallbackContext) -> None:
    answer = update.message.text
    question = context.user_data.pop('input_question', None) or context.user_data.pop('text_question', None)
    if not question:
        return

    if update.message.chat_id not in List_Of_Students_Statistics:
        List_Of_Students_Statistics[update.message.chat_id] = [0, 0]
    List_Of_Students_Statistics[update.message.chat_id][1] += 1
    correct_answer = question['answer'].strip().lower()
    user_answer = answer.strip().lower()
    if user_answer == correct_answer:
        response = '✅*Верно!*✅'
        response += f"\n\n✍Твой ответ:\n\n{answer}"
        List_Of_Students_Statistics[update.message.chat_id][0] += 1
    else:
        response = '❌*Неверно.*❌'
        response += f"\n\n✍Твой ответ:\n\n{answer}"

    response_message = (
        f"{question['question']}\n\n{response}\n\n🟢*Правильный ответ*:🟢\n\n{question['answer']}"
    )

    if 'comment' in question:
        response_message += f"\n\n{question['comment']}"

    context.user_data.pop('input_question_active', None)
    context.user_data.pop('text_question_active', None)

    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message, parse_mode='Markdown')

# Обработчик ответа на тестовое задание
def test_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if update.effective_chat.id not in List_Of_Students_Statistics:
        List_Of_Students_Statistics[update.effective_user.id] = [0, 0]

    if data == "submit":
        selected_options = context.user_data.get("selected_options", set())
        question = context.user_data.get("multichoice_question")

        if question is None:
            query.edit_message_text(text="Произошла ошибка, попробуйте снова.")
            return

        if len(selected_options) == 0:
            query.answer(text="Выберите хотя бы один вариант!", show_alert=True)
            return

        correct_answers = set(question["correct"])

        if selected_options == correct_answers:
            response_message = (
                f"{question['question']}\n\n✅*Правильно!✅ Твои ответы*:\n\n" +
                "\n".join(question['options'][i] for i in selected_options)
            )
            List_Of_Students_Statistics[update.effective_user.id][0] += 1
            List_Of_Students_Statistics[update.effective_user.id][1] += 1
        else:
            correct_answers_text = "\n".join(question["options"][i] for i in correct_answers)
            selected_answers_text = "\n".join(question["options"][i] for i in selected_options)

            response_message = (
                f"{question['question']}\n\n❌*Неверно.❌ Твои ответы:*\n\n{selected_answers_text}\n\n\n🟢*Правильные ответы*:🟢\n\n{correct_answers_text}"
            )
            List_Of_Students_Statistics[update.effective_user.id][1] += 1

        if 'comment' in question and question['comment']:
            response_message += f"\n\n{question['comment']}"

        query.edit_message_text(text=response_message, parse_mode='Markdown')

        context.user_data.pop("multichoice_question", None)
        context.user_data.pop("selected_options", None)
        context.user_data.pop("multichoice_question_active", None)
        return

    answer_index = int(data.split(":")[0])
    selected = data.split(":")[1] == "True"

    question = context.user_data.get("multichoice_question")
    selected_options = context.user_data.get("selected_options")

    if question is None or selected_options is None:
        query.edit_message_text(text="Произошла ошибка, попробуйте снова.")
        return

    if selected:
        selected_options.discard(answer_index)
    else:
        selected_options.add(answer_index)

    keyboard = [
        [
            InlineKeyboardButton(
                ("✅ " if i in selected_options else "➖") + opt,
                callback_data=f"{i}:{i in selected_options}",
            )
        ]
        for i, opt in enumerate(question["options"])
    ]

    keyboard.append([InlineKeyboardButton("Проверить ответы", callback_data="submit")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_reply_markup(reply_markup)

# обработчик команды Contact to support
def contact_to_support(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его.")
    #     return
    if str(update.message.chat_id) == str(MY_CHAT_ID):
        contact_support(update, context)
    else:
        context.user_data['current_menu'] = None
        context.user_data['awaiting_contact_message'] = True
        update.message.reply_text('Введите сообщение или загрузите фото, которое вы хотите отправить в поддержку:')

# отдельный обработчик для поддержки
def contact_support(update: Update, context: CallbackContext) -> None:
    context.user_data['current_menu'] = None
    context.user_data['awaiting_contact_message'] = True
    if len(List_Of_Students_Answers) == 0:
        update.message.reply_text("Пока нету доступных сообщений")
        answer_id = -1
        return
    update.message.reply_text(f'Всего доступно сообщений: {len(List_Of_Students_Answers)}. \n Для проверки какого-то из них, напишите номер интересующей посылки.')
    list_of_answers = ""
    cnt = 1
    for key, value in List_Of_Students_Answers.items():
        list_of_answers += f'{cnt}. '
        list_of_answers += List_Of_Students_Answers[key][:20] + "..."
        list_of_answers += "\n"
        cnt += 1
    update.message.reply_text(list_of_answers)

# Обработчик команды Contact
def contact(update: Update, context: CallbackContext) -> None:
    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его.")
    #     return
    if str(update.message.chat_id) == str(MY_CHAT_ID):
        contact_teacher(update, context)
    else:
        context.user_data['current_menu'] = None
        context.user_data['awaiting_contact_message'] = True
        update.message.reply_text('Введите сообщение или загрузите фото, которое вы хотите отправить на проверку:')

# Отдельный обработчик Contact для проверки
def contact_teacher(update: Update, context: CallbackContext) -> None:
    context.user_data['current_menu'] = None
    context.user_data['awaiting_contact_message'] = True
    if len(List_Of_Students_Answers) == 0:
        update.message.reply_text("Пока нету доступных посылок")
        answer_id = -1
        return
    update.message.reply_text(f'Всего доступно посылок: {len(List_Of_Students_Answers)}. \n Для проверки какого-то из них, напишите номер интересующей посылки.')
    list_of_answers = ""
    cnt = 1
    for key, value in List_Of_Students_Answers.items():
        list_of_answers += f'{cnt}. '
        list_of_answers += List_Of_Students_Answers[key][:20] + "..."
        list_of_answers += "\n"
        cnt += 1
    update.message.reply_text(list_of_answers)

# Обработчик отправки сообщения учителю
def forward_message_to_or_for_teacher(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_contact_message', False):
        if str(update.message.chat_id) == MY_CHAT_ID:
            if update.message.text:
                user_message = update.message.text
                cnt = 1
                global answer_id
                answer_id = -1
                for key, value in List_Of_Students_Answers.items():
                    if cnt == int(user_message):
                        answer_id = key
                        break
                    cnt += 1
                update.message.reply_text(f'Ответ ученика: \n\n{List_Of_Students_Answers[answer_id]}')
                update.message.reply_text("Напишите ответ или пришлите фото ответа")
                context.user_data['awaiting_teacher_answer'] = True

            context.user_data['awaiting_contact_message'] = False
        else:
            if update.message.text:
                user_message = update.message.text
                context.bot.send_message(
                    chat_id=MY_CHAT_ID,
                    text=f"Новое сообщение: {user_message[:20]}..."
                )
                List_Of_Students_Answers[update.message.chat_id] = user_message
                update.message.reply_text('Ваше сообщение было успешно отправлено на проверку.')
            elif update.message.photo:
                photo_file_id = update.message.photo[-1].file_id
                photo_caption = update.message.caption if update.message.caption else ""
                context.bot.send_photo(
                    chat_id=MY_CHAT_ID,
                    photo=photo_file_id,
                    caption=f"Новое фото: {photo_caption}"
                )
                List_Of_Students_Answers[update.message.chat_id] = "Фотография"
                update.message.reply_text('Ваше фото было успешно отправлено на проверку.')

            context.user_data['awaiting_contact_message'] = False
    else:
        if context.user_data.get("input_question_active"):
            check_input(update, context)
        elif context.user_data.get("awaiting_teacher_answer", False):
            message_for_student(update, context)
        elif context.user_data.get("text_question_active"):
            check_input(update, context)
        elif context.user_data.get("multichoice_question_active"):
            check_input(update, context)
        elif context.user_data.get("current_menu") in ["ОГЭ", "ЕГЭ"]:
            send_test(update, context)
        else:
            update.message.reply_text(
                "Сообщение не было отправлено на проверку и не является командой для выполнения теста."
            )

# Ответ ученику на его посылку
def message_for_student(update: Update, context: CallbackContext) -> None:

    if update.message.text:
        user_message = update.message.text
        context.bot.send_message(
            chat_id=answer_id,
            text=f"Новый ответ от проверки:\n {user_message}"
        )
    elif update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        photo_caption = update.message.caption if update.message.caption else ""
        context.bot.send_photo(
            chat_id=answer_id,
            photo=photo_file_id,
            caption=f"Новый ответ от проверки:\n {photo_caption}"
        )

    List_Of_Students_Answers.pop(answer_id)
    update.message.reply_text('Ваш ответ был успешно отправлен.')

# Обработчик для статистики
def get_bank(update: Update, context: CallbackContext) -> None:

    # Проверка незавершенных заданий
    # if context.user_data.get('input_question_active') or context.user_data.get('text_question_active') or context.user_data.get('multichoice_question_active'):
    #     update.message.reply_text("Вы не выполнили прошлое задание. Завершите его")
    #     return

    if len(List_Of_Students_Statistics) != 0:
        if List_Of_Students_Statistics[update.message.chat_id][1] != 0:
            update.message.reply_text(f'Ваша статистика:\nПравильно выполнено: {List_Of_Students_Statistics[update.message.chat_id][0]}\n'
                                      f'Всего выполнено: {List_Of_Students_Statistics[update.message.chat_id][1]}\n'
                                      f'Процент правильных ответов: {round(List_Of_Students_Statistics[update.message.chat_id][0] / List_Of_Students_Statistics[update.message.chat_id][1] * 100, 2)}%')
        else:
            update.message.reply_text("Вы еще не начинали выполнять ни одного задания!")
    else:
        update.message.reply_text("Вы еще не начинали выполнять ни одного задания!")
    context.user_data['awaiting_contact_message'] = False
    start(update, context)
