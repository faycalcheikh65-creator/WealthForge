import requests
import os
from flask import current_app
from flask_mail import Message, Mail
import random
import string

mail = Mail()

def send_telegram_message(message, parse_mode='HTML'):
    try:
        token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
        if not token or not chat_id:
            return None
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': parse_mode}
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")
        return None

def generate_reset_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def validate_wallet_address(address):
    if not address:
        return False
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False
