from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class AboutForm(FlaskForm):  # Форма для изменения данных аккаунта
    name = StringField('Изменение имени', validators=[DataRequired()])
    surname = StringField('Изменение фамилии', validators=[DataRequired()])
    about_me = TextAreaField('О себе', validators=[DataRequired()])
    submit = SubmitField('Применить')
