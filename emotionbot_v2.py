# -*- coding: utf-8 -*-
import random

from telegram import ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)

import logging
import numpy as np
import json

from constants import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING1, CHOOSING2, TYPING_REPLY = range(3)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{}: \n{}'.format(key, '\n'.join(value)))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    reply_text = "Привет! Надеюсь, у тебя всё хорошо. "
    reply_text += "Как ты себя сейчас чувствуешь?"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING1


def regular_choice1(update, context):
    text = update.message.text.upper()
    context.user_data['choice1'] = text
    reply_text = 'Ты испытываешь {}?'.format(text)
    update.message.reply_text(reply_text)
    print(text)
    if text in ['СТЫД', 'ВИНА']:
        print('мы тута')
        msg = "Помни, что чувства стыда и вины - это социальные чувства. Попробуй описать причину этих чувств."
        update.message.reply_text(msg)
        return TYPING_REPLY
    msg = 'Давай попробуем более конкретно сформулировать твою эмоцию:'
    update.message.reply_text(msg, reply_markup=markups[text.upper()])
    return CHOOSING2


def regular_choice2(update, context):
    text = update.message.text.upper()
    context.user_data['choice2'] = text
    if context.user_data.get(text):
        reply_text = 'Ты уже испытывал {}, вот твое описание этого: \n{}\n' \
                     'Расскажи, почему ты испытываешь это ' \
                     'сейчас? Напиши одним сообщением.'.format(text, "\n".join(context.user_data[text]))
    else:
        reply_text = 'Ты испытываешь {}? Расскажи, почему? Напиши одним сообщением.'.format(text)
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def received_information(update, context):
    text = update.message.text
    category = context.user_data['choice1']
    print(category)
    print(text)
    print(context.user_data)
    if context.user_data.get(category):
        context.user_data[category] += [text]
    else:
        context.user_data[category] = [text]
    print(context.user_data[category])
    nice_words = ["Всё нормас!"]
    try:
        with open("nice_words_data.json", encoding="utf-8") as nice_words_file:
            nice_words_data = json.load(nice_words_file)
            nice_words = nice_words_data[category]
            # nice_words = nice_words[np.random.randint(0, len(nice_words))]
    except:
        pass
    update.message.reply_text("Хорошо, я тебя услышал! {}".format(random.choice(nice_words)),
                              reply_markup=markup, parse_mode=ParseMode.HTML)

    del context.user_data['choice1']
    del context.user_data['choice2']

    return CHOOSING1


def show_data(update, context):
    update.message.reply_text("Вот что ты мне уже рассказал:"
                              "{}".format(facts_to_str(context.user_data)))


def show_help(update, context):

    update.message.reply_text(text="Тебе сложно определиться с тем, какие эмоции и чувства ты испытываешь? "
                              "Держи список, который поможет тебе разобраться!"
                              "{}".format(EMOTIONS),
                              parse_mode=ParseMode.HTML)


def done(update, context):
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
        # print(json_data)
        token = json_data["TOKEN"]
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='emotionbot_v2')
    updater = Updater(token, persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY

    def get_str_list_of_emotions(rk):
        return "|".join([x for l in rk for x in l])
    regex_str1 = get_str_list_of_emotions(reply_keyboard)
    regex_str_anger = get_str_list_of_emotions(reply_keyboard_anger)
    regex_str_sadness = get_str_list_of_emotions(reply_keyboard_sadness)
    regex_str_happiness = get_str_list_of_emotions(reply_keyboard_happiness)
    regex_str_fear = get_str_list_of_emotions(reply_keyboard_fear)
    regex_str2 = "|".join(
        [regex_str_anger, regex_str_sadness, regex_str_fear, regex_str_happiness]
    )

    print(regex_str1)
    print(regex_str2)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING1: [MessageHandler(Filters.regex('^({})$'.format(regex_str1)), regular_choice1)],
            CHOOSING2: [MessageHandler(Filters.regex('^({})$'.format(regex_str2)), regular_choice2)],
            TYPING_REPLY: [MessageHandler(Filters.text, received_information), ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
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
