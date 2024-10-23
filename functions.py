import random
import requests
import diskcache
from datetime import datetime, timedelta

cache = diskcache.Cache('bot_cache_dir')

WEBAPP_BASEURL = "https://telegram-mini-app-api-m2uy.onrender.com"


quiz_data = [
    {"id": 1, "question": "What is the capital of France?", "options": ["Paris", "Berlin", "Madrid"], "answer": "Paris"},
    {"id": 2, "question": "What is 2 + 2?", "options": ["3", "4", "5"], "answer": "4"},
    {"id": 3, "question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter"], "answer": "Mars"},
    {"id": 4, "question": "Who wrote 'Romeo and Juliet'?", "options": ["William Shakespeare", "Mark Twain", "Charles Dickens"], "answer": "William Shakespeare"},
    {"id": 5, "question": "What is the largest ocean on Earth?", "options": ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean"], "answer": "Pacific Ocean"},
    {"id": 6, "question": "What is the square root of 64?", "options": ["6", "8", "10"], "answer": "8"},
    {"id": 7, "question": "Which element's chemical symbol is 'O'?", "options": ["Oxygen", "Osmium", "Gold"], "answer": "Oxygen"},
    {"id": 8, "question": "Who painted the Mona Lisa?", "options": ["Leonardo da Vinci", "Vincent van Gogh", "Pablo Picasso"], "answer": "Leonardo da Vinci"},
    {"id": 9, "question": "What is the smallest country in the world?", "options": ["Vatican City", "Monaco", "Malta"], "answer": "Vatican City"},
    {"id": 10, "question": "Which continent is the Sahara Desert located in?", "options": ["Africa", "Asia", "Australia"], "answer": "Africa"}
]


def get_user(user_id: str) -> dict:
    url = f"{WEBAPP_BASEURL}/api/users/"
    try:
        response = requests.get(url, headers={"TELEGRAM-USER-ID": user_id})
        user_data = response.json()
    except Exception as err:
        print("🔥🔥🔥🔥 Exception = ", err)
        user_data = {}
    return user_data


def create_referral(user_id: str, referral_code: str):
    url = f"{WEBAPP_BASEURL}/api/refer/"
    try:
        data = {
            "referred": str(user_id),
            "referrer": str(referral_code),
        }
        response = requests.post(url, json=data, headers={"TELEGRAM-USER-ID": str(user_id)})
        referral_data = response.json()
    except Exception as err:
        print("🔥🔥🔥🔥 Exception = ", err)
        referral_data = {}
    return referral_data


def get_random_question(user_id: str) -> dict:
    url = f"{WEBAPP_BASEURL}/api/question/"
    try:
        response = requests.get(url, headers={"TELEGRAM-USER-ID": user_id})
        question_data = response.json()
    except Exception:
        pass
    else:
        return question_data
    return quiz_data[random.randint(0, len(quiz_data) - 1)]


def get_question(question_id: str, user_id: str) -> dict:
    url = f"{WEBAPP_BASEURL}/api/question/{question_id}/"
    try:
        response = requests.get(url, headers={"TELEGRAM-USER-ID": user_id})
        question_data = response.json()
    except Exception:
        pass
    else:
        return question_data
    for q in quiz_data:
        if q['id'] == question_id:
            question =  q
    return question   


def increment_user_question_count(user_id: str) -> int:
    user_question_count = cache.get(f"{user_id}_question_count", 1)
    current_question_count = user_question_count + 1
    cache.set(f"{user_id}_question_count", current_question_count, expire=seconds_until_next_day())
    return current_question_count


def seconds_until_next_day() -> int:
    now = datetime.now()
    next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    time_difference = next_day - now
    return int(time_difference.total_seconds())


