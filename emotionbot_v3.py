# -*- coding: utf-8 -*-
import json
import logging
import random
from datetime import datetime

from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['СТРАХ', 'ПЕЧАЛЬ'],
    ['ГНЕВ', 'РАДОСТЬ'],
    ['СТЫД', 'ВИНА']
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        date = value[0].strftime("%Y-%m-%d %H:%M")
        text = value[1]
        facts.append('{}: \n{}\n{}'.format(key, date, text))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    reply_text = "Привет! Надеюсь, у тебя всё хорошо. "
    if context.user_data:
        reply_text += "Ты уже рассказал мне о своих эмоциях ({}). Что ты " \
                      "чувствуешь сейчас?".format(", ".join(context.user_data.keys()))
    else:
        reply_text += "Как ты себя сейчас чувствуешь?"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text.upper()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = 'Ты уже испытывал {}, вот твое описание этого: \n{}\n' \
                     'Расскажи, почему ты испытываешь это ' \
                     'сейчас?'.format(text, context.user_data[text])
        print(context.user_data[text])
    else:
        reply_text = 'Ты испытываешь {}? Расскажи, почему?'.format(text)
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def received_information(update, context):
    text = update.message.text
    category = context.user_data['choice']
    print(category)
    print(text)
    print(context.user_data)
    data = [datetime.now(), text]
    if context.user_data.get(category):
        context.user_data[category] += data
    else:
        context.user_data[category] = data
    print(context.user_data[category])
    del context.user_data['choice']
    with open("nice_words_data.json", encoding="utf-8") as nice_words_file:
        nice_words_data = json.load(nice_words_file)
        nice_words = nice_words_data[category]
    update.message.reply_text("Хорошо, я тебя услышал! {}".format(random.choice(nice_words)),
                              reply_markup=markup, parse_mode=ParseMode.HTML)

    update.message.reply_text("А как ты себя чувствуешь сейчас?")

    return CHOOSING


def show_data(update, context):
    update.message.reply_text("Вот что ты мне уже рассказал:"
                              "{}".format(facts_to_str(context.user_data)))

    return CHOOSING


def show_help(update, context):
    with open("emotions_data.json", encoding="utf-8") as emotions_list_file:
        emotions = ""
        emotions_data = json.load(emotions_list_file)
        print(emotions_data)
        for x in emotions_data:
            emotions += "\n<b>" + x + "</b>:\n"
            for y in emotions_data[x]:
                emotions += y + "\n"
    update.message.reply_text(text="Тебе сложно определиться с тем, какие эмоции и чувства ты испытываешь? "
                              "Держи список, который поможет тебе разобраться!"
                              "{}".format(emotions),
                              parse_mode=ParseMode.HTML)


def stop(update, context):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    update.message.reply_text("Вот что ты мне уже рассказал:"
                              "{}"
                              "До встреч!".format(facts_to_str(context.user_data)))
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Set up token and proxy
    with open("config.json") as json_file:
        json_data = json.load(json_file)
        token = json_data["TOKEN"]
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='emotionbot_v3')
    updater = Updater(token, persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    regex_str = "|".join([x for l in reply_keyboard for x in l])
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^({})$'.format(regex_str)), regular_choice)],
            TYPING_CHOICE: [MessageHandler(Filters.text, regular_choice)],
            TYPING_REPLY: [MessageHandler(Filters.text, received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), stop)],
        name="my_conversation",
        persistent=True
    )

    dp.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data)
    dp.add_handler(show_data_handler)

    help_handler = CommandHandler('help', show_help)
    dp.add_handler(help_handler)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
