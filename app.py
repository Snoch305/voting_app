from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Создаем папку static если её нет
os.makedirs('static', exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    pesel = db.Column(db.String(11), unique=True, nullable=False)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    votes = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    if Candidate.query.count() == 0:
        candidates = [
            Candidate(name="Władimir Putin"),
            Candidate(name="Aleksander Łukaszenka"),
            Candidate(name="Wołodymyr Zełenskyj"),
            Candidate(name="Kasim-Żomart Tokajew"),
            Candidate(name="Andrzej Duda")
        ]
        db.session.add_all(candidates)
        db.session.commit()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('result'))
    return render_template('index.html')

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        try:
            username = request.form['username'].lower()
            password = request.form['password']
            email = request.form['email']
            full_name = request.form['full_name']
            birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d')
            city = request.form['city']
            pesel = request.form['pesel']

            if not pesel.isdigit() or len(pesel) != 11:
                return render_template('register.html', error="PESEL musi składać się z 11 cyfr!")

            if User.query.filter_by(username=username).first():
                return render_template('register.html', error="Użytkownik już istnieje!")
            if User.query.filter_by(email=email).first():
                return render_template('register.html', error="Email już istnieje!")
            if User.query.filter_by(pesel=pesel).first():
                return render_template('register.html', error="PESEL już istnieje!")

            new_user = User(
                username=username, password=password, email=email,
                full_name=full_name, birthdate=birthdate, city=city, pesel=pesel
            )
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('result'))
        
        except Exception as e:
            return render_template('register.html', error=f"Wystąpił błąd: {str(e)}")

    return render_template('register.html')

# Страница голосования
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('register_user'))

    if request.method == 'POST':
        candidate_id = request.form.get('candidate')
        if not candidate_id:
            return render_template('vote.html', 
                               candidates=Candidate.query.all(),
                               error="Proszę wybrać kandydata!")
            
        candidate = Candidate.query.get(candidate_id)
        
        if 'voted_users' in session and session['username'] in session['voted_users']:
            return redirect(url_for('result'))
            
        if candidate:
            candidate.votes += 1
            if 'voted_users' not in session:
                session['voted_users'] = []
            session['voted_users'].append(session['username'])
            db.session.commit()
            return redirect(url_for('result'))
    
    return render_template('vote.html', candidates=Candidate.query.all())

# Страница результатов
@app.route('/result')
def result():
    sorted_candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
    return render_template('result.html', 
                         sorted_candidates=sorted_candidates,
                         username=session.get('username'))

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('voted_users', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)