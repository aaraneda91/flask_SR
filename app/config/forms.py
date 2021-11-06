from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
   username = StringField('Nombre usuario', validators=[DataRequired()])
   password = PasswordField('Contraseña', validators=[DataRequired()])
   remember_me = BooleanField('Recuérdame')
   submit = SubmitField('Login')