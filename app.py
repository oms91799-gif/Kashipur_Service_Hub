from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "kashipur_super_secret"
# Database path for Render/Local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kashipur_v5.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20)) # 'Customer' / 'Worker'
    service = db.Column(db.String(100))
    rate = db.Column(db.String(50), default="Discuss on call")
    bio = db.Column(db.Text, default="Kashipur Professional")
    status = db.Column(db.String(20), default='Offline')
    is_verified = db.Column(db.Boolean, default=False) # Admin will verify
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/customer')
def customer_portal():
    category = request.args.get('category')
    # Sirf Online workers dikhenge
    if category:
        workers = User.query.filter_by(role='Worker', service=category, status='Online').all()
    else:
        workers = User.query.filter_by(role='Worker', status='Online').all()
    return render_template('customer_home.html', workers=workers, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            new_user = User(
                name=request.form['name'],
                phone=request.form['phone'],
                password=request.form['password'],
                role=request.form['role'],
                service=request.form.get('service'),
                rate=request.form.get('rate'),
                bio=request.form.get('bio')
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return "Phone number already exists!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(phone=request.form['phone'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            if user.phone == "9999999999": # Aapka Admin Number set karein
                return redirect(url_for('admin_panel'))
            return redirect(url_for('worker_dashboard' if user.role == 'Worker' else 'customer_portal'))
    return render_template('login.html')

@app.route('/worker_dashboard')
def worker_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    worker = User.query.get(session['user_id'])
    worker.last_seen = datetime.utcnow()
    db.session.commit()
    return render_template('worker_panel.html', worker=worker)

@app.route('/toggle_status')
def toggle_status():
    worker = User.query.get(session['user_id'])
    worker.status = 'Online' if worker.status == 'Offline' else 'Offline'
    db.session.commit()
    return redirect(url_for('worker_dashboard'))

# --- ADMIN PANEL ---
@app.route('/admin_panel')
def admin_panel():
    if 'user_id' not in session: return redirect(url_for('login'))
    users = User.query.all()
    return render_template('admin_panel.html', users=users)

@app.route('/verify/<int:uid>')
def verify(uid):
    user = User.query.get(uid)
    user.is_verified = not user.is_verified
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
