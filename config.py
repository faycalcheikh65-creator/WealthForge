import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wealthforge.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    SITE_NAME = os.getenv('SITE_NAME', 'WealthForge')
    SITE_URL = os.getenv('SITE_URL', 'http://localhost:5000')
    MIN_DEPOSIT = float(os.getenv('MIN_DEPOSIT', 2.0))
    MIN_WITHDRAW = float(os.getenv('MIN_WITHDRAW', 10.0))
    REFERRAL_BONUS = float(os.getenv('REFERRAL_BONUS', 2.5))
    
    BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
    WALLET_ADDRESS = "0x0db7207915a5e075a2fbe51216c326a0f703d33a"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
