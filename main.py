import telebot
from telebot import types

operators = []  #список из id операторов

mytoken = ''
bot = telebot.TeleBot(mytoken)


@bot.message_handler(commands=["data"]) #получить информацию из сообщения в тг
def data(message):
    bot.send_message(message.chat.id, str(message.reply_to_message)[:4096])


@bot.message_handler(commands=["help"]) #помощь для пользователя
def help(message):
    bot.send_message(message.chat.id, "Напишите нам, если вам понадобится помощь: @[тут будет контакт оператора]")


@bot.message_handler(commands=["start", "reg"]) #"регистрация" для пользователя
def start(message):
    bot.send_message(message.chat.id, "[Приветственное сообщение для пользователя]. \n\nИнформация по командам:\n"
                                      "Чтобы сдать задание, напишите /pass\nЧтобы получить помощь, напишите /help\n\n"
                                      "<b>Для подтверждения участия напишите мне ваши фамилию и имя</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, reg_confirming, bot)    #ждем от пользователя фамилию и имя

def reg_confirming(message, bot):
    bot.send_message(message.chat.id, "Отлично! Ждите своего первого задания, оно появится в течение нескольких дней.")

    for oper_id in operators:   #отправляем всем операторам id и ФИ пользователя (это операторам надо будет сохранить)
        bot.send_message(oper_id, f"Пользователь <code>{message.chat.id}</code> с ФИО <b>{message.text}</b> ждет своего "
                                  f"первого задания.\n Напишите <code>/send {message.chat.id} [текст задания]</code>,"
                                  f" чтобы его отправить.", parse_mode='HTML')

pictures = []#хранит значения фоток
albums_id = {} #словарь для обработки альбомов
flag = {} #флаг для того, чтобы дать команду боту, когда нужно записывать фотки (true), а когда нет

@bot.message_handler(commands=["pass"]) #сдать задание
def pass_task(message): 
        bot.send_message(message.chat.id, "Отправьте, пожалуйста, фотографии выполнения задания, а также формулировку "
                                      "задания в одном сообщении. После сообщения с фотографиями пришлите /got")
        pictures.clear()
        global flag
        if message.chat.id not in flag:
            flag[message.chat.id] = True
        bot.register_next_step_handler(message, get_task, bot)
        
@bot.message_handler(commands=["got"]) #пользователь прислал полностью задания
def pass_task(message):
        global flag
        if message.chat.id not in flag:
            bot.send_message(message.chat.id, "Сначала вам нужно получить задание, ожидайте)")
            return
        bot.send_message(message.chat.id, "Успешно отправлено! Ожидайте следующего задания!")
        bot.send_message(123457689, f"Пользователь <b>{message.chat.id}</b> досдал задание:", parse_mode='HTML') 
        if len(pictures):
            bot.send_media_group(123457689,pictures)
            pictures.clear()
        flag[message.chat.id] = False

def get_task(message, bot):
    if message.content_type not in ['photo','document']:
        bot.send_message(message.chat.id, "Вы не приложили фотографии :(\nЧтобы сдать задание, напишите /pass еще раз")
        return

    try:
        message.json['caption'] #проверяем, что у сообщения есть текст

    except Exception as e:
        bot.send_message(message.chat.id, "Похоже, что вы не добавили описание задания :(\nЧтобы сдать задание, "
                                          "напишите /pass еще раз ")
        return
        
    #for oper_id in operators:
    bot.send_message(123457689, f"Пользователь <b>{message.chat.id}</b> сдал задание:", parse_mode='HTML')
    bot.forward_message(123457689, message.chat.id, message.message_id)   #вот эта штука отправляет только 1 фото
    #bot.send_media_group(123457689, [types.InputMediaPhoto(message.photo[-1].file_id),types.InputMediaPhoto(message.photo[-2].file_id)])
    bot.send_message(123457689, f"Пользователь <b>{message.chat.id}</b> ждет следующего задания. Напишите <code>/send "
                                  f"{message.chat.id} [текст задания]</code>, чтобы его отправить.", parse_mode='HTML')
    


@bot.message_handler(content_types=["photo","document"])
def get_pictures(message):
    global flag
    # if flag==0:
        
    #     # keyboard = telebot.types.InlineKeyboardMarkup()
    #     # button_yes = telebot.types.InlineKeyboardButton(text="Да",
    #     #                                              callback_data='get_pictures')
    #     # button_no = telebot.types.InlineKeyboardButton(text="Нет",
    #     #                                              callback_data='dont_get_pictures')
    #     # keyboard.add(button_yes, button_no)
    # else:

    if hasattr(message,'media_group_id'):
        gr_id = message.media_group_id
        global albums_id
        if gr_id not in albums_id:
            albums_id[gr_id] = True
            if message.chat.id not in flag or not flag[message.chat.id]: bot.send_message(message.chat.id,"Очень крутые фотографии! Но, кажется, они не относятся к текущему заданию")
        pictures.append(types.InputMediaPhoto(message.photo[0].file_id))
    


# @bot.callback_query_handler(func = lambda call: call.data == 'get_pictures')
# def callback_get_pictures(message):
#     global flag
#     flag = 1
    
@bot.message_handler(commands=["send_album"]) #отправить альбом пользователю
def send_album(message):
    pass

# обработка команды /send
def send(message):
    command, id = message.text.split(' ')[0], message.text.split(' ')[1]

    if command != '/send' or (not id.isdigit()):    #проверяем корректность команды
        bot.send_message(message.chat.id, "<b>Неверный формат команды.</b>\nКоманда должна выглядеть следующим образом:\n"
                                          "/send [id пользователя] [текст задания]\n Отправьте команду еще раз.", parse_mode='HTML')
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    confirm_btn = types.InlineKeyboardButton(text='Подтвердить', callback_data=f'confirm:{id}')
    cancel_btn = types.InlineKeyboardButton(text='Отмена', callback_data=f'cancel')
    markup.add(confirm_btn, cancel_btn)
    bot.send_message(message.chat.id, f'Вы хотите отправить пользователю <b>{id}</b> следующее задание: '
                                      f'{message.text.replace(f"/send {id} ", '')}', reply_markup=markup, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def text_received(message):
    if '/send' in message.text and message.chat.id in operators:    #отдельно тут обрабатываем команду /send
        send(message)
        return

    bot.send_message(message.chat.id, 'Такой команды я не знаю:(')


#BUTTON PROCESSING
@bot.callback_query_handler(func = lambda call:True)
def buttons(call):
    if call.data.startswith('confirm'):
        target_id = call.data.replace('confirm:','')
        message_text = call.message.text.replace(f'Вы хотите отправить пользователю {target_id} следующее задание: ','')

        bot.send_message(int(target_id), '<b>Ваше новое задание:</b>\n' + message_text + '\n\nЧтобы сдать его, напишите /pass', parse_mode='HTML')
        bot.edit_message_text(f'Пользователю {target_id} было отправлено задание: {message_text}', call.message.chat.id,
                              message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    elif call.data == 'cancel':
        bot.edit_message_text('Отправление отменено', call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    else:
        bot.send_message(call.message.chat.id, 'Необработанная кнопка')
        bot.answer_callback_query(call.id)

bot.polling(none_stop=True, interval=0)