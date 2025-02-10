from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for user sessions & flash messages
db = SQLAlchemy(app)

# User Model with Password Hashing
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Stores hashed password

# Good Deed Model
class GoodDeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    date = db.Column(db.Date, default=datetime.now)  # Uses local time
    description = db.Column(db.String(255), nullable=False)
    quran_read = db.Column(db.Boolean, default=False)
    prayers_offered = db.Column(db.Boolean, default=False)

# Create database tables
with app.app_context():
    db.create_all()

# Route for Login & Registration
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        if user:  # If user exists, verify password
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect('/dashboard')
            else:
                flash("Incorrect password. Try again!", "danger")
        else:  # If user does not exist, create account
            hashed_password = generate_password_hash(password)  # Hash password
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect('/dashboard')

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    deeds = GoodDeed.query.filter_by(user_id=user_id).order_by(GoodDeed.date.desc()).all()
    return render_template('index.html', deeds=deeds)

# Route for Adding a Good Deed
@app.route('/add', methods=['POST'])
def add_deed():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    description = request.form.get('description')
    quran_read = request.form.get('quran_read') == 'on'
    prayers_offered = request.form.get('prayers_offered') == 'on'

    if description:
        new_deed = GoodDeed(user_id=user_id, description=description, quran_read=quran_read, prayers_offered=prayers_offered)
        db.session.add(new_deed)
        db.session.commit()
    
    return redirect('/dashboard')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
 db.create_all() # This recreates tables with the correct structure
