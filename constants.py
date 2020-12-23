from telegram import ReplyKeyboardMarkup
import json

EMOTIONS = ""

with open("emotions_data.json", encoding="utf-8") as emotions_list_file:
    emotions_data = json.load(emotions_list_file)
for x in emotions_data:
    EMOTIONS += "\n<b>" + x + "</b>:\n"
    for y in emotions_data[x]:
        EMOTIONS += y + "\n"

reply_keyboard = [
    ['СТРАХ', 'ПЕЧАЛЬ'],
    ['ГНЕВ', 'РАДОСТЬ'],
    ['СТЫД', 'ВИНА']
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_sadness = [
    ["скорбь", "тоска", "уныние", "горе"],
    ["одиночество", "подавленность", "сожаление"],
    ["безнадёжность", "беспомощность", "отчаяние"],
    ["отверженность", "бессилие", "недовольство"],
    ["опустошённость"]
]
markup_sadness = ReplyKeyboardMarkup(reply_keyboard_sadness, one_time_keyboard=True)

reply_keyboard_happiness = [
    ["восторг", "любовь", "упоение", "восхищение"],
    ["приподнятость", "достоинство", "ликование"],
    ["наслаждение", "нежность", "блаженство"],
    ["благодарность", "увлечение", "умиротворение"],
    ["вдохновение", "надежда"]
]
markup_happiness = ReplyKeyboardMarkup(reply_keyboard_happiness, one_time_keyboard=True)

reply_keyboard_anger = [
    ["ярость", "бешенство", "ненависть", "злость"],
    ["ожесточение", "раздражение", "обида"],
    ["досада", "уязвлённость", "отвращение"],
    ["гневность", "зависть", "омерзение"],
    ["нетерпение", "неприязнь"]
]
markup_anger = ReplyKeyboardMarkup(reply_keyboard_anger, one_time_keyboard=True)

reply_keyboard_fear = [
    ["ужас", "боязнь", "тревога"],
    ["беспокойство", "удивление", "паника"],
    ["оцепенение", "испуг", "смятение"],
    ["растерянность", "недоверие", "робость"],
    ["замешательство", "неуверенность"]
]
markup_fear = ReplyKeyboardMarkup(reply_keyboard_fear, one_time_keyboard=True)

markups = {
    "СТРАХ": markup_fear,
    "ПЕЧАЛЬ": markup_sadness,
    "ГНЕВ": markup_anger,
    "РАДОСТЬ": markup_happiness
}
