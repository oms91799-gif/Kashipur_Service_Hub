from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "kashipur_ultra_premium_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kashipur_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Customer' / 'Worker'
    service = db.Column(db.String(100))
    rate = db.Column(db.String(50), default="Discuss on Call")
    bio = db.Column(db.Text, default="Kashipur's Verified Professional")
    status = db.Column(db.String(20), default='Offline')
    rating = db.Column(db.Float, default=4.8)
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
    if category:
        workers = User.query.filter_by(role='Worker', service=category, status='Online').all()
    else:
        workers = User.query.filter_by(role='Worker', status='Online').all()
    return render_template('customer_home.html', workers=workers, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(phone=request.form['phone'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)