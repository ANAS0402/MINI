# signals/telegram_bot.py
import requests

def send_telegram_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def get_updates(token):
    url = f'https://api.telegram.org/bot{token}/getUpdates'
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except Exception as e:
        return {'ok': False, 'error': str(e)}
