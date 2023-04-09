from aiogram import Bot, Dispatcher, executor, types

# видео файл один и отправлятся в двух разных меню

# сюда имя бота
bot = Bot("")

dp = Dispatcher(bot)

course_completion_markup = types.InlineKeyboardMarkup()
course_completion_markup.add(
    types.InlineKeyboardButton("Да", callback_data="yes"),
    types.InlineKeyboardButton("Нет", callback_data="no"),
)

# списки с ответами
list_questions_markups = []
for level in [
    [
        ["1", "wrong"],
        ["2", "wrong"],
        ["3", "right_1"],
        ["4", "wrong"],
    ],
    [
        ["1", "wrong"],
        ["2", "wrong"],
        ["3", "wrong"],
        ["4", "right_2"],
    ],
]:
    markup = types.InlineKeyboardMarkup()
    for item in level:
        markup.add(types.InlineKeyboardButton(item[0], callback_data=item[1]))
    list_questions_markups.append(markup)


list_questions = [
    "Выберите правильный ответ (вопрос 1).",
    "Выберите правильный ответ (вопрос 2).",
]

# словарь с пользователями
dict_users = {}

# класс пользователя
class class_user:
    def __init__(self):
        self.count = 0
        self.course_is_completed = False
        # видео перед вопросом будет показываться только один раз
        self.video_is_get = False

    def count_change(self, item):
        self.count = int(item.split("_")[1])


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global dict_users

    # если пользователь успешно ответил на все вопросы то повторить он уже не может (зачем ему он же уже прошел)
    if (
        dict_users.get(message.chat.id)
        and dict_users[message.chat.id].course_is_completed
    ):
        await message.answer("Вы успешно прошли курс!")
    else:
        await message.answer("Приветствую.")
        await message.answer_video(open("video.mp4", "rb"))
        await message.answer("Начать курс?", reply_markup=course_completion_markup)


@dp.callback_query_handler(lambda call: True)
async def callback(call):
    global dict_users
    user_id = call.message.chat.id

    if not dict_users.get(user_id):
        dict_users[user_id] = class_user()
    user = dict_users[user_id]

    # если пользователь успешно ответил на все вопросы то повторить он уже не может (зачем ему он же уже прошел)
    if user.course_is_completed:
        await bot.send_message(user_id, "Вы успешно прошли курс!")

    else:
        if call.data == "no":
            await bot.send_message(user_id, "Вы отказались проходить курс")

        elif call.data == "yes":
            if not user.video_is_get:
                await bot.send_video(user_id, video=open("video.mp4", "rb"))
                user.video_is_get = True

            await bot.send_message(
                user_id,
                list_questions[user.count],
                reply_markup=list_questions_markups[user.count],
            )

        elif call.data == "wrong":
            await bot.send_message(
                user_id,
                "Неверный ответ. Попробовать ещё раз?",
                reply_markup=course_completion_markup,
            )

        elif "right" in call.data:
            user.count_change(call.data)

            if user.count == len(list_questions):
                user.course_is_completed = True
                await bot.send_message(user_id, "Вы успешно прошли курс!")
            else:

                await bot.send_message(
                    user_id,
                    list_questions[user.count],
                    reply_markup=list_questions_markups[user.count],
                )


executor.start_polling(dp)
