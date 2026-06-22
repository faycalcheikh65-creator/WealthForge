from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import bcrypt
import random
import string

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    full_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(200), nullable=False)
    
    is_owner = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    
    balance = db.Column(db.Float, default=0.0)
    total_deposit = db.Column(db.Float, default=0.0)
    total_withdraw = db.Column(db.Float, default=0.0)
    
    referral_code = db.Column(db.String(20), unique=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_count = db.Column(db.Integer, default=0)
    
    last_task_at = db.Column(db.DateTime, nullable=True)
    last_weekly_profit_at = db.Column(db.DateTime, nullable=True)
    tasks_completed = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def can_do_task(self):
        if not self.last_task_at:
            return True
        return datetime.utcnow() - self.last_task_at >= timedelta(hours=24)
    
    def generate_referral_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_total_deposit(self):
        return db.session.query(db.func.sum(Deposit.amount)).filter(
            Deposit.user_id == self.id,
            Deposit.status == 'confirmed'
        ).scalar() or 0

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tx_hash = db.Column(db.String(100))
    proof_image = db.Column(db.String(200))
    wallet_address = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='deposits', lazy=True)

class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    wallet_address = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='withdraws', lazy=True)

class TaskLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_type = db.Column(db.String(50))
    reward = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='tasks', lazy=True)

class ReferralBonus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, default=2.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    referrer = db.relationship('User', foreign_keys=[referrer_id], lazy=True)
    referred = db.relationship('User', foreign_keys=[referred_id], lazy=True)
