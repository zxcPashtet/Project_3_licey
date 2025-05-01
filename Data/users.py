import sqlalchemy
from .db_session import SQlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SQlAlchemyBase, UserMixin, SerializerMixin):  # Описание модели данных 'users'
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    totp_secret = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    avatar = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    topic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about_me = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):  # Создание хэшированного пароля
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # Проверка хэшированного пароля
        return check_password_hash(self.hashed_password, password)
