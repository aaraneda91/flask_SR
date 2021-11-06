from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DateField, IntegerField, HiddenField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import PasswordInput
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import Clients, Communes, Campaigns, UsersCategory, Institutions, LinkTypes, ConnectionTypes, Users, ClientsCategory
from datetime import datetime
from flask_moment import Moment


moment = Moment()

def enabled_clients():
	return Clients.query.order_by(Clients.name).all()

def enabled_communes():
	return Communes.query.order_by(Communes.name).all()

def enabled_campaigns():
	return Campaigns.query.all()

def enabled_users_category():
	return UsersCategory.query.all()

def enabled_institutions():
	return Institutions.query.all()

def enabled_link_types():
	return LinkTypes.query.all()

def enabled_connection_types():
	return ConnectionTypes.query.all()

def enabled_directors():
	directors = Users()
	return directors.get_directors()

def enabled_clients_categories():
	return ClientsCategory.query.all()

class RegisterCommunesForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=64)])

class EditCommunesForm(FlaskForm):
	name_before= HiddenField('name_before')
	name_after = StringField(validators=[DataRequired(), Length(max=64)])

# registrar nuevo cliente
class RegisterClientsForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=64)])
	directors = QuerySelectField(query_factory=enabled_directors, allow_blank=True)
	categories = QuerySelectField(query_factory=enabled_clients_categories, allow_blank=True)

# registrar nueva categoria de cliente
class RegisterClientsCategoriesForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=80)])

class RegisterInstitutionsForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=64)])
	address = StringField(validators=[DataRequired(), Length(max=64)])
	commune = QuerySelectField(query_factory=enabled_communes, allow_blank=True, validators=[DataRequired()])
	client = QuerySelectField(query_factory=enabled_clients, allow_blank=True, validators=[DataRequired()])

class EditInstitutionsForm(FlaskForm):
	institution_id = HiddenField('institution_id')
	name = StringField(validators=[DataRequired(), Length(max=64)])
	address = StringField(validators=[DataRequired(), Length(max=64)])
	commune = QuerySelectField(query_factory=enabled_communes, allow_blank=True, validators=[DataRequired()])
	client = StringField("client")
	submit = SubmitField('Guardar cambios')

class ImportInstitutionsForm(FlaskForm):
	client = QuerySelectField(query_factory=enabled_clients, allow_blank=True, validators=[DataRequired()])
	upload = FileField('file')

class EditLocalContactForm(FlaskForm):
	institution = StringField(validators=[Length(max=64)])
	name = StringField(validators=[Length(max=64)])
	phone = StringField(validators=[Length(max=64)])
	email = StringField(validators=[Length(max=64)])

class ImportLocalContactsForm(FlaskForm):
	client = QuerySelectField(query_factory=enabled_clients, allow_blank=True, validators=[DataRequired()])
	upload = FileField('file')

# formularios para creación de campañas

class RegisterCampaignsForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=64)])
	client = QuerySelectField(query_factory=enabled_clients, allow_blank=True, validators=[DataRequired()])
	period = IntegerField(
		validators=[
			DataRequired(), 
			Length(min=0, max=9999)
		], 
		default=datetime.now().year)

# usuarios

class RegisterUsersForm(FlaskForm):
	username = StringField('Nombre usuario', validators=[DataRequired(), Length(max=64)])
	name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
	lastname = StringField('Apellido', validators=[DataRequired(), Length(max=64)])
	email = StringField('Correo', validators=[Length(max=64)])
	password = PasswordField('Contraseña', validators=[DataRequired(), Length(max=64)])
	repeat_password = PasswordField('Repetir contraseña', validators=[DataRequired(), Length(max=64)])
	categories = QuerySelectField(query_factory=enabled_users_category, allow_blank=True, validators=[DataRequired()])
	is_admin = BooleanField('Administrador')
	submit = SubmitField('Registrar')

class UpdateUserForm(FlaskForm):
	user_id = HiddenField('user_id')
	username = StringField('Nombre usuario', validators=[DataRequired(), Length(max=64)], render_kw={"placeholder": "Nombre de usuario"})
	name = StringField('Nombre', validators=[DataRequired(), Length(max=64)], render_kw={"placeholder": "Nombre"})
	lastname = StringField('Apellido', validators=[DataRequired(), Length(max=64)], render_kw={"placeholder": "Apellido"})
	email = StringField('Correo', validators=[Length(max=64)], render_kw={"placeholder": "Correo electrónico"})
	category = QuerySelectField(query_factory=enabled_users_category, allow_blank=True)
	is_admin = BooleanField('Administrador')
	submit = SubmitField('Guardar cambios')

class UpdatePasswordForm(FlaskForm):
	password = StringField('Contraseña', validators=[DataRequired(), Length(max=150)], widget=PasswordInput(hide_value=False), render_kw={"placeholder": "Contraseña"})
	repeat_password = StringField('Repetir contraseña', validators=[DataRequired(), Length(max=150)], widget=PasswordInput(hide_value=False), render_kw={"placeholder": "Repetir contraseña"})
	user_id = HiddenField('user_id')

class RegisterLinkTypesForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=80)])

class RegisterConnectionTypesForm(FlaskForm):
	name = StringField(validators=[DataRequired(), Length(max=80)])

class RegisterLinksForm(FlaskForm):
	service_code = StringField('Código de servicio', validators=[DataRequired(), Length(max=64)])
	ip_direction = StringField('Dirección ip', validators=[Length(max=15)])
	#link_type = QuerySelectField(query_factory=enabled_link_types, validators=[DataRequired()])
	#connection_type = QuerySelectField(query_factory=enabled_connection_types,allow_blank=True)
	link_type = SelectField("Tipo de enlace")
	connection_type = SelectField("Tipo de conexión")
	institution = SelectField(validators=[DataRequired()])
	clients = SelectField("Clientes")

class ImportLinksForm(FlaskForm):
	client = QuerySelectField(query_factory=enabled_clients, allow_blank=True, validators=[DataRequired()])
	upload = FileField('file')

class EditLinksForm(FlaskForm):
	link_id = HiddenField('link_id')
	service_code = StringField('Código de servicio', validators=[DataRequired(), Length(max=64)])
	ip_direction = StringField('Dirección ip', validators=[Length(max=15)])
	link_type = QuerySelectField(query_factory=enabled_link_types, validators=[DataRequired()])
	connection_type = QuerySelectField(query_factory=enabled_connection_types,allow_blank=True)
	institution = StringField('Establecimiento')

class RegisterGroupsMailsForm(FlaskForm):
	name = StringField('Nombre del grupo', validators=[DataRequired(), Length(max=200)])
	submit = SubmitField('Crear grupo')

class EditGroupsMailsForm(FlaskForm):
	name = StringField('Nombre del grupo', validators=[DataRequired(), Length(max=200)])
	submit = SubmitField('Gardar cambios')

class RegisterItemGroupsMailsForm(FlaskForm):
	name = StringField('Nombre', validators=[Length(max=200)])
	mail = StringField('Correo', validators=[DataRequired(), Length(max=150)])
	submit = SubmitField('Registrar contacto')

class RegisterClientsGroupsMailsForm(FlaskForm):
	clients = QuerySelectField(query_factory=enabled_clients, allow_blank=False, validators=[DataRequired()])
	submit = SubmitField('Registrar cliente')