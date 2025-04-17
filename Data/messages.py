import sqlalchemy
from .db_session import SQlAlchemyBase


class Message(SQlAlchemyBase):
    __tablename__ = 'messages'
    id1_id2 = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    messages = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    background_id1 = sqlalchemy.Column(sqlalchemy.String, default='ordinary')
    background_id2 = sqlalchemy.Column(sqlalchemy.String, default='ordinary')
    dates = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    messages_id1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    messages_id2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)