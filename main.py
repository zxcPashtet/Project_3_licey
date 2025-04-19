from flask import Flask, render_template, redirect, request, abort, send_file
from Data import db_session
from Data.users import User
from Data.messages import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from form.register import RegisterForm
from form.login import LoginForm
from form.aboutme import AboutForm
from os.path import join, dirname, realpath
import io


app = Flask(__name__)
app.config['SECRET_KEY'] = 'zxcmodePashtetAndShniga'
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static\\img')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    return redirect('/login')


@app.route('/image/<int:image_id>')
def get_image(image_id):
    db_sess = db_session.create_session()
    img = db_sess.query(User).filter((User.id == image_id)).first()
    return send_file(io.BytesIO(img.avatar), mimetype='image/png')


@app.route('/main/<int:id>', methods=['GET', 'POST'])
@login_required
def main_page(id):
    db_sess = db_session.create_session()

    created_chats = db_sess.query(Message).filter(((getattr(Message, 'id1_id2').ilike(f'{current_user.id}_%')) |
                                                   (getattr(Message, 'id1_id2').ilike(f'%_{current_user.id}')))).all()
    created_chats_users = []
    for i in created_chats:
        if i.id1_id2.split('_')[0] == str(current_user.id):
            id_enemy = i.id1_id2.split('_')[1]
        else:
            id_enemy = i.id1_id2.split('_')[0]
        created_chats_users.append(db_sess.query(User).filter(User.id == id_enemy).all()[0])

    users = db_sess.query(User).filter((User.id == id)).first()
    background = users.topic.split()
    form = AboutForm()
    if request.method == "GET":
        users = db_sess.query(User).filter((User.id == id)).first()
        if users:
            form.name.data = users.name
            form.surname.data = users.surname
            form.about_me.data = users.about_me
        else:
            abort(404)
    if form.validate_on_submit():
        if users:
            users.name = form.name.data
            users.surname = form.surname.data
            users.about_me = form.about_me.data
            db_sess.commit()
            return redirect(f'/main/{current_user.id}')
        else:
            abort(404)
    if request.method == 'POST':
        if request.form.get("light_tema"):
            background = ['#808080;', '#808080;', '#808080;', '#808080;']
            users = db_sess.query(User).filter((User.id == id)).first()
            if users:
                users.topic = ' '.join(background)
                db_sess.commit()
            return render_template('main.html', form=form, background=background,
                                   created_chats_users=created_chats_users)

        if request.form.get("night_tema"):
            background = ['#23282b;', '#1d334a;', '#4a545c;', '#979aaa;']
            users = db_sess.query(User).filter((User.id == id)).first()
            if users:
                users.topic = ' '.join(background)
                db_sess.commit()
            return render_template('main.html', form=form, background=background,
                                   created_chats_users=created_chats_users)

        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            avatar_data = file.read()
            avatar_users = db_sess.query(User).filter((User.id == id)).first()
            if avatar_users:
                avatar_users.avatar = avatar_data
                db_sess.commit()
            return render_template('main.html', form=form, background=background,
                                   created_chats_users=created_chats_users)

        if request.form.get('search'):
            result = request.form['search']
            found_users = db_sess.query(User).filter((getattr(User, 'login').ilike(f'{result}%')) &
                                                     (User.login != current_user.login)).all()
            return render_template('main.html', form=form, found_users=found_users,
                                   background=background)

        if request.form.get('user-button'):
            global chat, selected_user
            button_value = request.form.get('user-button')
            db_sess = db_session.create_session()
            selected_user = db_sess.query(User).filter(User.login == button_value).all()
            chat = db_sess.query(Message).filter((Message.id1_id2 == f'{current_user.id}_{selected_user[0].id}') |
                                                  (Message.id1_id2 == f'{selected_user[0].id}_{current_user.id}')).first()
            if not chat:
                new_chat = Message()
                new_chat.id1_id2 = f'{current_user.id}_{selected_user[0].id}'
                new_chat.messages = ''
                db_sess.add(new_chat)
                db_sess.commit()
                chat = new_chat
            return render_template('main.html', form=form, background=background,
                                   chat=chat, selected_user=selected_user[0],
                                   created_chats_users=created_chats_users)

        if request.form.get('input-field'):
            try:
                print('' if chat else '')
            except:
                return render_template('main.html', form=form, background=background,
                                       created_chats_users=created_chats_users)
            if request.form.get('input-field') != "'" and request.form.get('input-field') != '"':
                tab_messages = chat.messages
                chat = db_sess.query(Message).filter(Message.id1_id2 == chat.id1_id2).all()[0]
                chat.messages = tab_messages + (f'---{current_user.id}:{request.form.get("input-field")}')
                if chat.id1_id2.split('_')[0] == str(current_user.id):
                    chat.messages_id1 += 1
                    chat.messages_id2 = 0
                else:
                    chat.messages_id2 += 1
                    chat.messages_id1 = 0
                db_sess.commit()
            return render_template('main.html', form=form, background=background,
                                    chat=chat, selected_user=selected_user[0], created_chats_users=created_chats_users)

    return render_template('main.html', form=form, background=background,
                           created_chats_users=created_chats_users)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter((User.email == form.email.data) | (User.login == form.login.data)).first():
            return render_template('register.html', title='Регистрация', form=form, message='Такой пользователь уже есть')
        with open('static/img/maxresdefault.jpg', 'rb') as img_file:
            avatar_data = img_file.read()
        user = User(
            login=form.login.data,
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            avatar=avatar_data,
            topic='#23282b #1d334a #4a545c #979aaa',
            about_me='Пока пусто'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect(f'/main/{user.id}')
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
            return redirect(f'/main/{current_user.id}')
        return render_template('login.html', form=form, message='Неправльный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init('db/forproject3.db')
    app.run()


if __name__ == '__main__':
    main()
    #db_session.global_init('db/forproject3.db')