from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class VerifyForm(FlaskForm):  # Форма для проверки кода двойной верификации
    otp = StringField('Код двухфакторной аунтефикации', validators=[DataRequired()])
    submit = SubmitField('Войти')