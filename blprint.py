import flask
from flask_login import login_required, current_user
from flask import jsonify, make_response, request
from Data import db_session
from Data.users import User
from Data.messages import Message
import datetime

blueprint = flask.Blueprint(
    'Gchat_api',
    __name__,
    template_folder='templates'
)
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'zxcmodePashtetAndShniga'


@blueprint.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    db_sess = db_session.create_session()
    chats = db_sess.query(Message).filter(((getattr(Message, 'id1_id2').ilike(f'{current_user.id}_%')) |
                                           (getattr(Message, 'id1_id2').ilike(f'%_{current_user.id}')))).all()
    return jsonify(
        {
            'chats':
                [item.to_dict(only=('id1_id2', 'messages', 'dates', 'messages_id1', 'messages_id2'))
                 for item in chats]
        }
    )


@blueprint.route('/api/chat/<string:id1_id2>', methods=['GET'])
@login_required
def get_chat(id1_id2):
    db_sess = db_session.create_session()
    chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                         (
                                                 Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
    if chat:
        return jsonify(
            {
                'chat':
                    chat.to_dict(only=('id1_id2', 'messages', 'dates', 'messages_id1', 'messages_id2'))
            }
        )
    else:
        return make_response(jsonify({'error': 'Not found chat'}), 404)


@blueprint.route('/api/chat/<string:id1_id2>/messages', methods=['GET'])
@login_required
def get_chat_messages(id1_id2):
    db_sess = db_session.create_session()
    chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                         (
                                                 Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
    if chat:
        return jsonify(
            {
                'chat_messages':
                    [{item: chat.messages.split('���')[item]} for item in range(2, len(chat.messages.split('���')) - 1)]
            }
        )
    else:
        return make_response(jsonify({'error': 'Not found chat'}), 404)


@blueprint.route('/api/chat/<string:id1_id2>/message/<int:index>', methods=['GET'])
@login_required
def get_chat_mess(id1_id2, index):
    db_sess = db_session.create_session()
    chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                         (
                                                 Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
    if chat:
        print(index, len(chat.messages) - 1)
        if len(chat.messages.split('���')) - 2 >= index:
            return jsonify(
                {
                    'chat_message':
                        {index: chat.messages.split('���')[index]}
                }
            )
        else:
            return make_response(jsonify({'error': 'Not found message'}), 404)
    else:
        return make_response(jsonify({'error': 'Not found chat'}), 404)


@blueprint.route('/api/users', methods=['GET'])
@login_required
def users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'login', 'email', 'surname', 'name', 'topic', 'about_me'))
                 for item in users]
        }
    )


@blueprint.route('/api/user/<int:index>', methods=['GET'])
@blueprint.route('/api/user/<string:index>', methods=['GET'])
@login_required
def user(index):
    db_sess = db_session.create_session()
    if str(index).isdigit():
        user = db_sess.query(User).filter(User.id == index).first()
    else:
        user = db_sess.query(User).filter(User.login == index).first()
    if user:
        return jsonify(
            {
                'user':
                    user.to_dict(only=('id', 'login', 'email', 'surname', 'name', 'topic', 'about_me'))
            }
        )
    else:
        return make_response(jsonify({'error': 'Not found user'}), 404)


@blueprint.route('/api/new_message/<string:id1_id2>/<string:message>', methods=['POST', 'GET'])
@login_required
def new_message(id1_id2, message):
    if (message not in ['"', "'", '', ' ']):
        db_sess = db_session.create_session()
        chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                             (
                                                     Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
        if not chat:
            new_chat = Message()
            new_chat.id1_id2 = id1_id2
            new_chat.messages = '0⁞m1���0⁞m2���'
            new_chat.dates = 'd1���d2���'
            db_sess.add(new_chat)
            db_sess.commit()
            chat = new_chat
        tab_messages = chat.messages
        tab_dates = chat.dates
        if tab_messages[-2].split('⁞')[
            1] != 'USER_HAS_BLOCKED_THIS_CHAT' and '⁞' not in message and '���' not in message:
            chat.messages = tab_messages + (f'{current_user.id}⁞{message}���')
            chat.dates = tab_dates + (f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}���')
            if chat.id1_id2.split('_')[0] == str(current_user.id):
                chat.messages_id1 += 1
            else:
                chat.messages_id2 += 1
            db_sess.commit()
            return make_response(jsonify({'result': 'OK'}))
    else:
        return make_response(jsonify({'error': ' Bad Request'}), 400)


@blueprint.route('/api/edit_message/<string:id1_id2>/<int:index>/<string:message>', methods=['PUT', 'GET'])
@login_required
def edit_message(id1_id2, index, message):
    if (message not in ['"', "'", '', ' ']):
        db_sess = db_session.create_session()
        chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                             (
                                                     Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
        if chat:
            tab_messages = chat.messages.split('���')
            tab_dates = chat.dates.split('���')
            if tab_messages[-2].split('⁞')[
                1] != 'USER_HAS_BLOCKED_THIS_CHAT' and '⁞' not in message and '���' not in message:
                tab_messages[index] = tab_messages[index].split('⁞')[0] + '⁞' + message
                tab_dates[index] = (
                    f'Изменено {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                chat.messages = '���'.join(tab_messages)
                chat.dates = '���'.join(tab_dates)
                db_sess.commit()
                return make_response(jsonify({'result': 'OK'}))
        else:
            return make_response(jsonify({'error': 'Not found chat'}), 404)
    else:
        return make_response(jsonify({'error': ' Bad Request'}), 400)


@blueprint.route('/api/delete_message/<string:id1_id2>/<int:index>', methods=['DELETE', 'GET'])
@login_required
def delete_message(id1_id2, index):
    db_sess = db_session.create_session()
    chat = db_sess.query(Message).filter((Message.id1_id2 == id1_id2) |
                                         (
                                                 Message.id1_id2 == f'{id1_id2.split("_")[1]}_{id1_id2.split("_")[0]}')).first()
    if chat:
        tab_messages = chat.messages.split('���')
        tab_dates = chat.dates.split('���')
        temp = tab_messages[int(index.split('��')[0])].split('⁞')[0]
        if chat.id1_id2.split('_')[0] == str(temp):
            chat.messages_id1 -= 1 if chat.messages_id1 != 0 else 0
        else:
            chat.messages_id2 -= 1 if chat.messages_id2 != 0 else 0
        del tab_messages[int(index.split('��')[0])]
        del tab_dates[int(index.split('��')[0])]
        chat.messages = '���'.join(tab_messages)
        chat.dates = '���'.join(tab_dates)
        db_sess.commit()
        return make_response(jsonify({'result': 'OK'}))
    else:
        return make_response(jsonify({'error': 'Not found chat'}), 404)
