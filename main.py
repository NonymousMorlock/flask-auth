from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
import uuid
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap5

from database import db
from models.user import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = '6545932b1d99bc1dcece4bfe55cdd14607c0604d39b7e575c0371a912092713c'
app.config['UPLOAD_FOLDER'] = 'static/files/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

bootstrap = Bootstrap5(app=app)
db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.filter_by(alternative_id=user_id).first()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            email=request.form.get('email'),
            password=request.form.get('password'),
            name=request.form.get('name'),
            alternative_id=str(uuid.uuid4())
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('secrets'))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.execute(db.select(User).where(User.email == email and User.password == password)).scalar()
        next_page = request.args.get('next')
        if not user:
            flash('Invalid credentials', 'warning')
            return redirect(url_for('login', next=next_page))
        login_user(user)
        return redirect(next_page or url_for('secrets'))
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", username=current_user.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
@login_required
def download():
    # as attachment will directly trigger a download intent...without that,
    # it'll open the file in your browser, I don't quite know for other file types, but this was the case for pdf
    # return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path='cheat_sheet.pdf', as_attachment=True)
    return send_from_directory(directory='static', path='files/cheat_sheet.pdf', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
