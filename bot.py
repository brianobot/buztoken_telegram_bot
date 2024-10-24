import json
import environ
import telebot
import diskcache
import logging

from telebot.types import Message
from telebot.types import WebAppInfo
from telebot.types import CallbackQuery
from telebot.types import KeyboardButton
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

import functions

env = environ.Env()
environ.Env.read_env()



API_TOKEN = env("API_TOKEN")
MAX_DAILY_QUESTION_COUNT = 70

bot = telebot.TeleBot(API_TOKEN)
cache = diskcache.Cache('bot_cache_dir')
logger = logging.getLogger(__name__)


START_COMMANDS = ["start", "hello", "init", "begin"]
USAGE_COMMANDS = [
    'start game 🎯'.title(), 
    'join the community'.title(), 
    'about us ℹ️'.title(),
]

FIRST_MESSAGE = """Hey {}! Welcome to Buzmode where 1 BUZ in-game = 1 BUZ coin at launch. 
The best part is that you won't have to wait forever for the token launch; 
it will happen a day before Christmas day to celebrate your riches! Got friends, family, colleagues? 
Bring them before time runs out, they’ll thank you later 
Tap 'About' to visit our website and learn more about what we're building.
"""

@bot.message_handler(commands=START_COMMANDS)
def send_welcome(message: Message):
    user_id = message.from_user.id
    user_data = functions.get_user(str(user_id))
    
    print("✅✅✅ User data = ", user_data)

    referral_code = None
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1]

    if referral_code:
        refer_response = functions.create_referral(message.from_user.id, referral_code)
        print("🇳🇬🇳🇬🇳🇬🇳🇬 Refer Response = ", refer_response)
    
    print(f"📊📊📊📊 {referral_code = }")
    # Create a reply keyboard markup
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn1 = KeyboardButton(USAGE_COMMANDS[0], web_app=WebAppInfo(url=f"https://telegram-mini-app-ui-1kw5.onrender.com?user_id={user_id}"))
    btn2 = KeyboardButton(USAGE_COMMANDS[1])
    btn3 = KeyboardButton(USAGE_COMMANDS[2])
   
    # Add buttons to the markup
    markup.add(btn1, btn2, btn3)

    # Send the welcome message along with the buttons
    bot.send_message(message.chat.id, FIRST_MESSAGE.format(user_id), reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text in USAGE_COMMANDS)
def handle_usage_commands(message: Message):
    text = message.text.lower()

    match text:
        case "start game 🎯":
            bot.reply_to(message, "Quiz Instructions 🎯\n- Type exit to End Quiz Session")
            start_game(message.from_user.id)
        case "join the community":
            markup = InlineKeyboardMarkup()
            join_button = InlineKeyboardButton("Join Our Channel", url="https://t.me/buzmode")
            markup.add(join_button)
            
            bot.reply_to(message, "Click the button below to join our Telegram channel:", reply_markup=markup)
        case "about us ℹ️":
            markup = InlineKeyboardMarkup()
            about_button = InlineKeyboardButton("About Us", url="https://twtr.to/Cvh31")
            markup.add(about_button)
            
            bot.reply_to(message, "Click to see About us", reply_markup=markup)
        case _:
            bot.reply_to(message, "🤷🏾‍♂️ I do not Understand this command, Type start to start again")


@bot.message_handler(commands=['config'])
def user_info(message: Message):
    user_data = functions.get_user(str(message.from_user.id))
    formatted_user_data = f"👤 **ID**: {user_data.get('id')},\n🐝 **Buz Tokens**: {user_data.get('buz_tokens', 0)},\n🧑‍🧒‍🧒 **Referrals**:  {user_data.get('referral_counts', 0)},"
    bot.reply_to(message, formatted_user_data, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def handle_answer_callback(call: CallbackQuery):
    callback_data: dict = json.loads(call.data)
    user_id = call.from_user.id

    question_id = callback_data.get("question_id")
    question_data = functions.get_question(question_id, str(user_id))
    question_answer = question_data.get("answer")

    current_question_count = functions.increment_user_question_count(str(user_id))
    # this handle the edge case not responding with status for last daily question
    if (current_question_count - 1) > MAX_DAILY_QUESTION_COUNT:
        bot.send_message(user_id, "Max Daily Question Exceed! 🥹")
        bot.answer_callback_query(call.id, "Max Daily Question Exceed! 🥹")
    else:
        status = "✅ Correct 🎉🥳🎊" if question_answer == callback_data.get('option') else "Incorrect ❌"
        bot.answer_callback_query(call.id, text=status)
        send_question(user_id, current_question_count)
    

def start_game(user_id: str):
    user_current_question_count = cache.get(f"{user_id}_question_count", 0)
    if user_current_question_count > MAX_DAILY_QUESTION_COUNT:
        bot.send_message(user_id, "Max Daily Question Exceed! 🥹")
    else:
        send_question(user_id, user_current_question_count + 1)


def send_question(user_id: str, question_count: int = 1):
    current_question = functions.get_random_question(str(user_id))
    print(f"✅✅✅✅ {current_question = }")
    current_question_text = current_question['question']
    current_question_options = current_question['options']

    # Create reply keyboard markup with options
    markup = InlineKeyboardMarkup(row_width=2)

    for option in current_question_options:
        option_data = {"question_id": current_question.get("id"), "option": option}
        option_button = InlineKeyboardButton(option, callback_data=json.dumps(option_data))
        markup.add(option_button)

    question_markup = f"Question {question_count}: {current_question_text}\nOptions: \n\n"
    bot.send_message(user_id, question_markup, reply_markup=markup)


bot.infinity_polling()
