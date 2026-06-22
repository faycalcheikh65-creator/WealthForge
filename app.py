from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os

from config import Config
from models import db, User, Deposit, Withdraw, TaskLog, ReferralBonus
from utils import send_telegram_message, generate_reset_code, validate_wallet_address

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            flash('كلمتا المرور غير متطابقتين', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم مسبقاً', 'danger')
            return redirect(url_for('register'))
        
        user = User(email=email)
        user.set_password(password)
        user.referral_code = user.generate_referral_code()
        
        db.session.add(user)
        db.session.commit()
        
        flash('تم التسجيل بنجاح!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_banned:
                flash('هذا الحساب محظور', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            
            if user.is_owner:
                return redirect(url_for('owner_panel'))
            elif user.is_admin:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        
        flash('بريد إلكتروني أو كلمة مرور غير صحيحة', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_owner:
        return redirect(url_for('owner_panel'))
    if current_user.is_admin:
        return redirect(url_for('admin_panel'))
    
    can_task = current_user.can_do_task()
    deposits = Deposit.query.filter_by(user_id=current_user.id).all()
    withdraws = Withdraw.query.filter_by(user_id=current_user.id).all()
    total_deposit = current_user.get_total_deposit()
    
    return render_template('dashboard.html',
                         user=current_user,
                         can_task=can_task,
                         deposits=deposits,
                         withdraws=withdraws,
                         total_deposit=total_deposit)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    wallet_address = "0x0db7207915a5e075a2fbe51216c326a0f703d33a"
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        tx_hash = request.form.get('tx_hash')
        
        if amount < 2.0:
            flash('الحد الأدنى هو 2 USDT', 'danger')
            return redirect(url_for('deposit'))
        
        deposit = Deposit(
            user_id=current_user.id,
            amount=amount,
            tx_hash=tx_hash,
            wallet_address=wallet_address,
            status='pending'
        )
        db.session.add(deposit)
        db.session.commit()
        
        send_telegram_message(f"🚨 إيداع جديد: {current_user.email} - {amount} USDT")
        
        flash('تم إرسال طلب الإيداع', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('deposit.html', wallet=wallet_address)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        wallet = request.form.get('wallet_address')
        
        if amount < 10.0:
            flash('الحد الأدنى للسحب هو 10 USDT', 'danger')
            return redirect(url_for('withdraw'))
        
        if amount > current_user.balance:
            flash('الرصيد غير كافٍ', 'danger')
            return redirect(url_for('withdraw'))
        
        if not validate_wallet_address(wallet):
            flash('عنوان المحفظة غير صحيح', 'danger')
            return redirect(url_for('withdraw'))
        
        withdraw = Withdraw(
            user_id=current_user.id,
            amount=amount,
            wallet_address=wallet,
            status='pending'
        )
        current_user.balance -= amount
        db.session.add(withdraw)
        db.session.commit()
        
        flash('تم تقديم طلب السحب', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('withdraw.html')

@app.route('/owner')
@login_required
def owner_panel():
    if not current_user.is_owner:
        flash('غير مصرح', 'danger')
        return redirect(url_for('dashboard'))
    
    pending_deposits = Deposit.query.filter_by(status='pending').all()
    stats = {
        'total_users': User.query.count(),
        'pending_deposits': len(pending_deposits)
    }
    
    return render_template('owner_panel.html', stats=stats, deposits=pending_deposits)

@app.route('/owner/confirm-deposit/<int:deposit_id>', methods=['POST'])
@login_required
def confirm_deposit(deposit_id):
    if not current_user.is_owner:
        return jsonify({'error': 'غير مصرح'}), 403
    
    deposit = Deposit.query.get_or_404(deposit_id)
    deposit.status = 'confirmed'
    deposit.confirmed_at = datetime.utcnow()
    
    user = User.query.get(deposit.user_id)
    user.balance += deposit.amount
    user.total_deposit += deposit.amount
    
    db.session.commit()
    
    flash('تم تأكيد الإيداع', 'success')
    return redirect(url_for('owner_panel'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin and not current_user.is_owner:
        flash('غير مصرح', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('admin_panel.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        owner_email = os.getenv('OWNER_EMAIL', 'admin@wealthforge.org')
        if not User.query.filter_by(email=owner_email).first():
            owner = User(
                email=owner_email,
                full_name='المالك',
                is_owner=True,
                is_admin=True,
                referral_code='OWNER001'
            )
            owner.set_password(os.getenv('OWNER_PASSWORD', 'Admin@123'))
            db.session.add(owner)
            db.session.commit()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
