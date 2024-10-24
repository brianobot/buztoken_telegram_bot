import random
import requests
import diskcache
from datetime import datetime, timedelta

cache = diskcache.Cache('bot_cache_dir')

WEBAPP_BASEURL = "https://telegram-mini-app-api-m2uy.onrender.com"


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


