from flask import Flask, render_template, redirect, request, abort, send_file, url_for
from Data import db_session
from Data.users import User
from Data.messages import Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from form.register import RegisterForm
from form.login import LoginForm
from form.verify import VerifyForm
from form.aboutme import AboutForm
from os.path import join, dirname, realpath
from pyotp import TOTP
import smtplib
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
@app.route('/main/<int:id>/<string:chat_id>', methods=['GET', 'POST'])
@login_required
def main_page(id, chat_id=None):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        created_chats = db_sess.query(Message).filter(((getattr(Message, 'id1_id2').ilike(f'{current_user.id}_%')) |
                                                       (getattr(Message, 'id1_id2').ilike(f'%_{current_user.id}')))).all()
        created_chats_users = {}
        for i in created_chats:
            if i.messages != '':
                if i.id1_id2.split('_')[0] == str(current_user.id):
                    id_enemy = i.id1_id2.split('_')[1]
                else:
                    id_enemy = i.id1_id2.split('_')[0]
                if i.id1_id2.split('_')[0] == id_enemy :
                    created_chats_users[db_sess.query(User).filter(User.id == id_enemy).all()[0]] = int(i.messages_id1)
                if i.id1_id2.split('_')[1] == id_enemy:
                    created_chats_users[db_sess.query(User).filter(User.id == id_enemy).all()[0]] = int(i.messages_id2)
            created_chats_users = sorted(created_chats_users.items(), key=lambda item: item[1], reverse=True)
            created_chats_users = dict(created_chats_users)
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
                background = ['#FDF4E3;', '#F9F9F9;', '#F2DDC6;', '#B39F7A;']
                users = db_sess.query(User).filter((User.id == id)).first()
                if users:
                    users.topic = ' '.join(background)
                    db_sess.commit()
                return render_template('main.html', form=form,
                                       background=background,
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats)

            if request.form.get("night_tema"):
                background = ['#23282b;', '#1d334a;', '#4a545c;', '#415a77;']
                users = db_sess.query(User).filter((User.id == id)).first()
                if users:
                    users.topic = ' '.join(background)
                    db_sess.commit()
                return render_template('main.html', form=form,
                                       background=background,
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats)

            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                avatar_data = file.read()
                avatar_users = db_sess.query(User).filter((User.id == id)).first()
                if avatar_users:
                    avatar_users.avatar = avatar_data
                    db_sess.commit()
                return render_template('main.html', form=form,
                                       background=background,
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats)

            if request.form.get('search'):
                result = request.form['search']
                found_users = {}
                for i in db_sess.query(User).filter(((getattr(User, 'login').ilike(f'{result}%')) &
                                                     (User.login != current_user.login) |
                                                     (getattr(User, 'email').ilike(f'{result}%')) &
                                                     (User.email != current_user.email))).all():
                    temp_chat = db_sess.query(Message).filter(((getattr(Message, 'id1_id2').ilike(f'{current_user.id}_{i.id}')) |
                                                       (getattr(Message, 'id1_id2').ilike(f'{i.id}_{current_user.id}')))).all()

                    if temp_chat:
                        if temp_chat[0].messages != '':
                            if str(temp_chat[0].id1_id2.split('_')[0]) == str(i.id):
                                found_users[i] = int(temp_chat[0].messages_id1)
                            else:
                                found_users[i] = int(temp_chat[0].messages_id2)
                        else:
                            found_users[i] = 'None'
                    else:
                        found_users[i] = 'None'
                return render_template('main.html', form=form,
                                       found_users=found_users,
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
                if chat.id1_id2.split('_')[0] == str(current_user.id):
                    chat.messages_id2 = 0
                else:
                    chat.messages_id1 = 0
                db_sess.commit()
                return render_template('main.html', form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ')

            if request.form.get('block'):
                tab_messages = chat.messages
                chat = db_sess.query(Message).filter(Message.id1_id2 == chat.id1_id2).all()[0]
                chat.messages = tab_messages + ('---USER_HAS_BLOCKED_THIS_CHAT')
                return render_template('main.html', form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ')

            if request.form.get('unblock'):
                chat = db_sess.query(Message).filter(Message.id1_id2 == chat.id1_id2).all()[0]
                chat.messages = chat.messages.split('---')[:-1]
                return render_template('main.html', form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ')
            if request.form.get('message_id'):
                global index
                index = request.form.get('message_id')
                return render_template('main.html',
                                       form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ',
                                       delete_or_edit=True)

            action = request.form.get('action')
            if action == 'edit':
                pass

            if action == 'delete':
                chat = db_sess.query(Message).filter(Message.id1_id2 == chat.id1_id2).all()[0]
                tab_messages = chat.messages.split('---')
                del tab_messages[int(index.split('--')[0])]
                chat.messages = '---'.join(tab_messages)
                db_sess.commit()
                return render_template('main.html',
                                       form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ')

            if request.form.get('input-field'):
                try:
                    print('' if chat else '')
                except:
                    return render_template('main.html', form=form,
                                           background=background,
                                           created_chats_users=created_chats_users,
                                       created_chats=created_chats)

                if (request.form.get('input-field') != "'" and request.form.get('input-field') != '"' and
                        request.form.get('input-field') != " "):
                    tab_messages = chat.messages
                    if tab_messages.split('---')[-1] != 'USER_HAS_BLOCKED_THIS_CHAT':
                        chat = db_sess.query(Message).filter(Message.id1_id2 == chat.id1_id2).all()[0]
                        chat.messages = tab_messages + (f'{current_user.id}:{request.form.get("input-field")}---')
                        if chat.id1_id2.split('_')[0] == str(current_user.id):
                            chat.messages_id1 += 1
                        else:
                            chat.messages_id2 += 1
                        db_sess.commit()
                    return redirect(url_for('main_page', id=current_user.id, chat_id=chat.id1_id2))
        if chat_id:
            chat = db_sess.query(Message).filter(Message.id1_id2 == chat_id).first()
            if chat:
                if int(chat.id1_id2.split('_')[0]) == int(current_user.id):
                    selected_user = db_sess.query(User).filter(User.id == int(chat.id1_id2.split('_')[1])).all()
                if int(chat.id1_id2.split('_')[1]) == int(current_user.id):
                    selected_user = db_sess.query(User).filter(User.id == int(chat.id1_id2.split('_')[0])).all()
                return render_template('main.html', form=form,
                                       background=background,
                                       chat=chat,
                                       selected_user=selected_user[0],
                                       created_chats_users=created_chats_users,
                                       created_chats=created_chats,
                                       chat_messages=chat.messages.split('---'),
                                       text=' ')
        else:
            return render_template('main.html', form=form,
                                   background=background,
                                   created_chats_users=created_chats_users,
                                   created_chats=created_chats)
    return redirect('/register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


def generate_otp(totp_secret: str):
    return TOTP(totp_secret).now()


def send_email(subject: str, body: str, from_addr: str, to_addr: str):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_addr, 'xzwt kunc faok rctx')
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)
    server.quit()


def generate_2fa_secret(length: int = 6) -> str:
    return secrets.token_urlsafe(length)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        otp = generate_2fa_secret()
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
            about_me='Пока пусто',
            totp_secret=otp
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect(f'/main/{current_user.id}')
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
            otp = generate_2fa_secret()
            login_user(user, remember=form.remember_me.data)
            send_email('OTP', otp, 'ega.firefox@gmail.com', form.email.data)
            return redirect(f'/verify/{otp}')
        return render_template('login.html', form=form, message='Неправильный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/verify/<string:otp>', methods=['POST', 'GET'])
def verify(otp):
    form = VerifyForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        print(user.id, user.email, otp)
        if user and form.otp.data == otp:
            return redirect(f'/main/{user.id}')
    return render_template('verify.html', form=form)


def main():
    db_session.global_init('db/forproject3.db')
    app.run()


if __name__ == '__main__':
    main()
    #db_session.global_init('db/forproject3.db')