from flask import Flask, render_template, redirect
from Data import db_session
from Data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from form.register import RegisterForm
from form.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zxcmodePashtetAndShniga'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message='Такой пользователь уже есть')
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, message='Неправльный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init('db/baza.db')
    app.run()


if __name__ == '__main__':
    main()