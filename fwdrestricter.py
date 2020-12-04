import telebot
import config
import json

bot = telebot.TeleBot(config.api_token)

try:
    datafile = open(config.data_file, "r")
    data = json.load(datafile)
    datafile.close()
except FileNotFoundError:
    data = {}


def save_data():
    data_file = open(config.data_file, "w")
    json.dump(data, data_file, ensure_ascii=False)


def check_format(message):
    fwd_id = None
    words = message.text.split(maxsplit=1)
    if len(words) == 2:
        try:
            fwd_id = int(words[-1])
        except ValueError:
            pass
    return fwd_id


@bot.message_handler(commands=["del_fwd_from"])
def cmd_del_fwd(message):
    admins = [x.user.id for x in bot.get_chat_administrators(message.chat.id)]
    if message.from_user.id not in admins:
        bot.reply_to(message, "Эта команда доступна только администраторам")
        return
    fwd_id = check_format(message)
    if fwd_id is None:
        bot.reply_to(message, "Формат команды: del_fwd_from <id>")
        return
    chat_id = str(message.chat.id)
    if chat_id in data.keys():
        data[chat_id].append(fwd_id)
        data[chat_id] = list(set(data[chat_id]))
    else:
        data[chat_id] = [fwd_id]
    save_data()
    bot.reply_to(message, "Теперь стираю форварды из {}".format(fwd_id))


@bot.message_handler(commands=["pass_fwd_from"])
def cmd_del_fwd(message):
    admins = [x.user.id for x in bot.get_chat_administrators(message.chat.id)]
    if message.from_user.id not in admins:
        bot.reply_to(message, "Эта команда доступна только администраторам")
        return
    fwd_id = check_format(message)
    if fwd_id is None:
        bot.reply_to(message, "Формат команды: pass_fwd_from <id>")
        return
    chat_id = str(message.chat.id)
    if chat_id in data.keys():
        data[chat_id].remove(fwd_id)
    save_data()
    bot.reply_to(message, "Теперь не стираю форварды из {}".format(fwd_id))


@bot.message_handler(commands=["list_del_ids"])
def cmd_del_fwd(message):
    admins = [x.user.id for x in bot.get_chat_administrators(message.chat.id)]
    if message.from_user.id not in admins:
        bot.reply_to(message, "Эта команда доступна только администраторам")
        return
    chat_id = str(message.chat.id)
    if chat_id in data.keys():
        bot.reply_to(message, "Стираю форварды из {}".format(", ".join([str(x) for x in data[chat_id]])))
    else:
        bot.reply_to(message, "Пока не стираю форварды ниоткуда")


@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice'])
def check_message(message):
    admins = [x.user.id for x in bot.get_chat_administrators(message.chat.id)]
    chat_id = str(message.chat.id)
    if message.from_user.id not in admins:
        if chat_id in data.keys() and message.forward_from_chat and message.forward_from_chat.id in data[chat_id]:
            bot.delete_message(message.chat.id, message.message_id)
    elif message.text == "del_this_fwd":
        if message.reply_to_message.forward_from_chat:
            fwd_id = message.reply_to_message.forward_from_chat.id
            if chat_id in data.keys():
                data[chat_id].append(fwd_id)
                data[chat_id] = list(set(data[chat_id]))
            else:
                data[chat_id] = [fwd_id]
            del(message.chat.id, message.reply_to_message.id)
            bot.reply_to(message, "Теперь стираю форварды из {}".format(fwd_id))


bot.remove_webhook()
bot.polling(none_stop=True)
