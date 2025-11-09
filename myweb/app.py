import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_registration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_event = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, nullable=False)
    lokasi = db.Column(db.String(100), nullable=False)
    gambar = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Event {self.nama_event}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')  # registered, attended, cancelled

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Anda harus login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
@login_required
def beranda():
    semua_event = Event.query.all()
    user_id = session['user_id']
    registered_events = [reg.event_id for reg in Registration.query.filter_by(user_id=user_id).all()]
    return render_template('beranda.html', events=semua_event, registered_events=registered_events)

@app.route('/profil')
@login_required
def profil():
    user_id = session['user_id']
    user = User.query.get(user_id)
    registrations = Registration.query.filter_by(user_id=user_id).all()
    registered_events = [reg.event for reg in registrations]
    return render_template('profil.html', user=user, registered_events=registered_events)

@app.route('/user/<username>')
def show_user_profil(username):
    return render_template('showuser.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username sudah ada.', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrasi berhasil. Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login berhasil.', 'success')
            return redirect(url_for('beranda'))
        flash('Username atau password salah.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

# CRUD Routes for Events
@app.route('/events')
@login_required
def events():
    semua_event = Event.query.all()
    return render_template('events.html', events=semua_event)

@app.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        nama_event = request.form['nama_event']
        deskripsi = request.form['deskripsi']
        tanggal = request.form['tanggal']
        lokasi = request.form['lokasi']
        gambar = None
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gambar = filename
        from datetime import datetime
        event_baru = Event(nama_event=nama_event, deskripsi=deskripsi, tanggal=datetime.strptime(tanggal, '%Y-%m-%dT%H:%M'), lokasi=lokasi, gambar=gambar)
        db.session.add(event_baru)
        db.session.commit()
        flash('Event berhasil ditambahkan.', 'success')
        return redirect(url_for('events'))
    return render_template('add_event.html')

@app.route('/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.nama_event = request.form['nama_event']
        event.deskripsi = request.form['deskripsi']
        event.tanggal = request.form['tanggal']
        event.lokasi = request.form['lokasi']
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                event.gambar = filename
        from datetime import datetime
        event.tanggal = datetime.strptime(event.tanggal, '%Y-%m-%dT%H:%M')
        db.session.commit()
        flash('Event berhasil diupdate.', 'success')
        return redirect(url_for('events'))
    return render_template('edit_event.html', event=event)

@app.route('/events/<int:id>/delete')
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('events'))

@app.route('/events/<int:id>')
@login_required
def event_detail(id):
    event = Event.query.get_or_404(id)
    registrations = Registration.query.filter_by(event_id=id).all()
    registered_users = [reg.user.username for reg in registrations]
    user_id = session['user_id']
    is_registered = Registration.query.filter_by(user_id=user_id, event_id=id).first() is not None
    return render_template('event_detail.html', event=event, registered_users=registered_users, is_registered=is_registered)

@app.route('/events/<int:id>/register')
@login_required
def register_event(id):
    event = Event.query.get_or_404(id)
    user_id = session['user_id']
    existing_registration = Registration.query.filter_by(user_id=user_id, event_id=id).first()
    if existing_registration:
        flash('Anda sudah terdaftar untuk event ini.', 'error')
    else:
        registration = Registration(user_id=user_id, event_id=id)
        db.session.add(registration)
        db.session.commit()
        flash('Pendaftaran event berhasil.', 'success')
    return redirect(url_for('event_detail', id=id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
