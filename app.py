from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Good Deed model
class GoodDeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    description = db.Column(db.String(255), nullable=False)
    quran_read = db.Column(db.Boolean, default=False)
    prayers_offered = db.Column(db.Boolean, default=False)
    tahajjud_offered = db.Column(db.Boolean, default=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    deeds = GoodDeed.query.filter_by(user_id=current_user.id).order_by(GoodDeed.date.desc()).all()
    return render_template('index.html', deeds=deeds)

@app.route('/add', methods=['POST'])
@login_required
def add_deed():
    description = request.form.get('description')
    quran_read = request.form.get('quran_read') == 'on'
    prayers_offered = request.form.get('prayers_offered') == 'on'
    tahajjud_offered = request.form.get('tahajjud_offered') == 'on'

    if description:
        new_deed = GoodDeed(
            user_id=current_user.id,
            description=description,
            quran_read=quran_read,
            prayers_offered=prayers_offered,
            tahajjud_offered=tahajjud_offered
        )
        db.session.add(new_deed)
        db.session.commit()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
