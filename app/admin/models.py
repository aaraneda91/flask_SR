from sqlalchemy.orm import backref
from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Time, DateTime, String, Boolean, Text, exists, engine, SmallInteger
from datetime import datetime
import re
from unicodedata import normalize
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.logs.models import LogInstitutionsStatus, LogCommunesName, LogLocalContact
from app.config.const_logger import STATUS_INSTITUTIONS
from unidecode import unidecode

class ClientsCategory(db.Model):
	__tablename__ = 'admin_clients_category'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)

	def __repr__(self):
		return self.name

	def get_categories(self):
		return ClientsCategory.query.all()

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

# tabla: admin_clients
# descripción: registro de clientes

class Clients(db.Model):
	__tablename__ = 'admin_clients'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	category_id = Column(Integer, ForeignKey('admin_clients_category.id'), nullable=True)
	category = db.relationship('ClientsCategory', backref=db.backref('clientscategory_clients', lazy='dynamic'))

	def __repr__(self):
		return self.name

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def get_by_id(self, id):
		result = Clients.query.filter_by(id = id).first()
		return result

	def get_id_by_name(self, name):
		return Clients.query.filter_by(name=name).first()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_client_by_campaign(self, id):
		return Clients.query.join(Campaigns).filter_by(id=id).first()

	def get_director_by_client(self, id):
		result = ClientsDirectors.query.filter_by(clients_id = id).first()
		return result

class ClientsDirectors(db.Model):
	__tablename__ = 'admin_clients_directors'
	id = Column(Integer, primary_key = True)
	clients_id = Column(Integer, ForeignKey('admin_clients.id'), nullable = True)
	clients = db.relationship('Clients', backref=db.backref('clientsdirectors_clients', lazy='dynamic'))
	directors_id = Column(Integer, ForeignKey('admin_users.id'), nullable = True)
	directors = db.relationship('Users', backref=db.backref('clientsdirectors_directors', lazy='dynamic'))
	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def save(self):
		#validar si existe director relacionado a cliente
		client_director = ClientsDirectors.query.filter_by(clients_id = self.clients_id).first()

		# si ya existe, se actualiza el director de servicios
		if client_director is not None:
			client_director.directors_id = self.directors_id
			db.session.commit()
		# si no existe, se inserta nuevo registro
		else:
			if not self.id:
				db.session.add(self)
			db.session.commit()

		return True

# tabla: admin_regions
# descripción: registro de regiones

class Regions(db.Model):
	__tablename__ = "admin_regions"
	id = Column(Integer, primary_key=True)
	name = Column(String(150), nullable=False)
	abbreviation  = Column(String(4), nullable=True)
	capital = Column(String(64), nullable=True)

	def __repr__(self):
		return self.name

# tabla: admin_provinces
# descripcion: registro de provincias

class Provinces(db.Model):
	__tablename__ = "admin_provinces"
	id = Column(Integer, primary_key=True)
	name = Column(String(150), nullable=False)
	regions_id = Column(Integer, ForeignKey('admin_regions.id'), nullable=False)
	regions = db.relationship('Regions', backref=db.backref('provinces_regions', lazy='dynamic'))

	def __repr__(self):
		return self.name
	
# tabla: admin_communes
# descripción: registro de comunas

class Communes(db.Model):
	__tablename__ = 'admin_communes'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=True)
	provinces_id = Column(Integer, ForeignKey('admin_provinces.id'), nullable=True)
	provinces = db.relationship('Provinces', backref=db.backref('communes_provinces', lazy='dynamic'))

	def __repr__(self):
		return self.name

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def setName(self, name_before):
		commune = Communes.query.filter_by(id=self.id).first()
		commune.name = self.name
		log_commune = LogCommunesName()
		log_commune.name_before = name_before
		log_commune.name_after = self.name
		log_commune.commune_id = commune.id
		log_commune.user_id = current_user.id
		log_commune.setLog()
		db.session.commit()
		return True

	def get_by_id(self, id):
		return Communes.query.get(id)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_by_name(self, name):
		return Communes.query.filter_by(name=name).first()
	
	# se normalizan los strings y luego se comparan
	def validate_exist(self, name):

		communes = Communes.query.order_by(Communes.name).all()

		for commune in communes:

			commune_db = re.sub(
			r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
			normalize( "NFD", str(commune.name)), 0, re.I).lower()

			commune_parameter = re.sub(
			r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
			normalize( "NFD", str(name)), 0, re.I).lower()

			if commune_db == commune_parameter:
				return commune.id
		return False

# tabla: admin_status_institutions
# descripción: registro de estados de los establecimientos

class InstitutionsStatus(db.Model):
	__tablename__ = 'admin_status_institutions'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=True)
	alias = Column(String(80), nullable=True)

	def __repr__(self):
		return self.alias

	def get_by_id(self, id):
		return Communes.query.get(id)

# tabla n:m admin_institutions_campaigns_comments

class InstitutionsCampaignsComments(db.Model):
	__tablename__ = 'admin_institutions_campaigns_comments'
	id = Column(Integer, primary_key=True)
	institution_campaign_id = Column(Integer, ForeignKey('admin_institutions_campaigns.id'))
	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('admin_institutionscampaignscomments_users', lazy='dynamic'))
	status_id = Column(Integer, ForeignKey('admin_status_institutions.id'), nullable=True)
	status = db.relationship('InstitutionsStatus',backref=db.backref('admin_institutionscampaignscomments_status_institutions', lazy='dynamic'))
	comment = Column(Text, nullable = True)
	created = Column(DateTime, nullable=False, default=datetime.utcnow)
	
	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

# tabla n:m admin_institutions_campaigns_files

class InstitutionsCampaignsFiles(db.Model):
	__tablename__ = 'admin_institutions_campaigns_files'
	id = Column(Integer, primary_key=True)
	institution_campaign_id = Column(Integer, ForeignKey('admin_institutions_campaigns.id'))
	institution_campaign = db.relationship('InstitutionsCampaigns',backref=db.backref('admin_institutionscampaignsfiles_institutions_campaigns', lazy='dynamic'))
	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('admin_institutionscampaignsfiles_users', lazy='dynamic'))
	status_id = Column(Integer, ForeignKey('admin_status_institutions.id'), nullable=True)
	status = db.relationship('InstitutionsStatus',backref=db.backref('admin_institutionscampaignsfiles_status_institutions', lazy='dynamic'))
	filename = Column(String(200), nullable = False)
	unique_filename = Column(String(200), nullable = False)
	created = Column(DateTime, nullable=False, default=datetime.utcnow)
	
	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_by_unique_filename(unique_filename):
		return InstitutionsCampaignsFiles.query.filter_by(unique_filename = unique_filename).first()

# tabla: admin_institutions
# descripción: registro de establecimientos

class Institutions(db.Model):
	__tablename__ = 'admin_institutions'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=True)
	address = Column(String(80), nullable=True)

	commune_id = Column(Integer, ForeignKey('admin_communes.id'))
	commune = db.relationship(
		'Communes', backref=db.backref('admin_communes', lazy='dynamic'))

	client_id = Column(Integer, ForeignKey('admin_clients.id'))
	client = db.relationship('Clients', backref=db.backref(
		'admin_institutions', lazy='dynamic'))

	status_id = Column(Integer, ForeignKey(
		'admin_status_institutions.id'), nullable=True)
	status = db.relationship('InstitutionsStatus', backref=db.backref(
		'admin_status_institutions', lazy='dynamic'))

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship(
		'Users', backref=db.backref('admin_users', lazy='dynamic'))

	date_coord = Column(Date, nullable=True)
	time_coord = Column(Time, nullable=True)

	active = Column(Boolean, default=True)
	links = db.relationship('Links', backref='institution', lazy='dynamic')

	def __repr__(self):
		return self.name

	def get_by_id(self, id):
		return Institutions.query.get(id)

	@staticmethod
	def get_institution(id):
		return Institutions.query.filter_by(id=id).first()

	def get_institution_by_name(self, name, client = None):
		if client == None:
			return Institutions.query.filter_by(name=name).first()
		else:
			return Institutions.query.filter_by(name=name, client_id=client).first()

	# establecimientos que no están en campaña activa
	def get_institutions_not_in_campaign(self, client):

		sql = """SELECT admin_institutions.*, admin_communes.name as commune from admin_institutions
				LEFT JOIN admin_institutions_campaigns ON admin_institutions_campaigns.institution_id = admin_institutions.id 
				LEFT JOIN admin_campaigns ON admin_campaigns.id = admin_institutions_campaigns.campaign_id
				LEFT JOIN admin_communes ON admin_communes.id = admin_institutions.commune_id
				WHERE (admin_institutions_campaigns.campaign_id IS NULL OR admin_campaigns.active = false)
				AND admin_institutions.client_id="""+str(client)+"""
				AND admin_institutions.status_id is null
				ORDER BY admin_institutions.name ASC"""

		result = db.engine.execute(sql)

		return result

	# lista de establecimientos por campaña
	def get_institutions_by_campaigns(self, campaign):
		institutions = Institutions.query.join(
			InstitutionsCampaigns).join(Campaigns).filter_by(id=campaign)
		return institutions

	def get_gestion(self):
		result = db.session.query(InstitutionsCampaigns).join(Institutions).filter(Institutions.status_id.in_(
			(STATUS_INSTITUTIONS['POR_GESTIONAR'], STATUS_INSTITUTIONS['ESCALADO'], STATUS_INSTITUTIONS['INCIDENTE'], STATUS_INSTITUTIONS['PRUEBA_FALLIDA']))).order_by(self.name).all()
		return result

	def get_revision(self):
		result = db.session.query(InstitutionsCampaigns).join(Institutions).filter(Institutions.status_id.in_(
			(STATUS_INSTITUTIONS['SIN_REVISAR'], STATUS_INSTITUTIONS['EN_REVISION']))).order_by(self.name).all()
		return result

	def get_coordinacion(self):
		result = db.session.query(InstitutionsCampaigns).join(Institutions).filter(Institutions.status_id.in_(
			(STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['COORDINADO']))).order_by(self.name).all()
		return result

	def get_ejecucion(self):
		result = db.session.query(InstitutionsCampaigns).join(Institutions).join(Campaigns).filter(Institutions.status_id.in_(
			(STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION'])), Campaigns.active == True).order_by(self.name).all()
		return result

	def get_terminados(self):
		result = db.session.query(InstitutionsCampaigns).join(Institutions).filter(Institutions.status_id.in_(
			(STATUS_INSTITUTIONS['PRUEBA_EXITOSA'], STATUS_INSTITUTIONS['EXITOSO_OBSERVACION']))).order_by(self.name).all()
		return result

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def update_active(self):
		institution = self.get_institution(self.id)
		institution.active = False
		db.session.commit()

	def set_status(self, date_coord=None, time_coord=None, campaign_institution_id=None, ticket_ar=None, current_user_id = None):
		institution = self.get_institution(self.id)

		from_status = institution.status_id
		to_status = self.status_id
		institution_campaign = db.session.query(
			InstitutionsCampaigns).get(campaign_institution_id)
		institution.status_id = self.status_id

		db.session.commit()

		log_status = LogInstitutionsStatus()
		log_status.from_status_id = from_status
		log_status.to_status_id = to_status
		log_status.institution_campaign = institution_campaign
		log_status.date_coord = date_coord
		log_status.time_coord = time_coord
		log_status.ticket_ar = ticket_ar
		if current_user_id is None:
			log_status.user_id = current_user.id
		else:
			log_status.user_id = current_user_id

		log_status.setLog()

		return from_status

	def finish_insts(self, institution_id, campaign_institution_id, current_user_id, discard=None):

		# se elimina su estado
		institution = Institutions.query.filter(Institutions.id == institution_id).first()
		tmp_from_status = institution.status_id
		institution.status_id = None
		institution.user_id = None
		db.session.commit()

		if discard:
			ic = InstitutionsCampaigns.query.filter(InstitutionsCampaigns.id == campaign_institution_id).first()
			ic.campaign_id = None
			ic.institution_id = None
			db.session.commit()

		#se registra el cambio de estado en el log
		log_status = LogInstitutionsStatus()
		log_status.from_status_id = tmp_from_status
		log_status.to_status_id = None
		log_status.institution__campaing_id = campaign_institution_id
		log_status.user_id = current_user_id
		log_status.setLog()

		return True

	def add_contact(self, name=None, phone=None, email=None):
		lc = LocalContact()
		lc.name = name
		lc.phone = phone
		lc.email = email
		lc.institution_id = self.id
		lc_id = lc.save()

		return lc_id

	# método que guarda fecha y hora de coordinación
	def set_coordination(self, date, time):
		institution = self.get_institution(self.id)
		institution.date_coord = date
		institution.time_coord = time

		try:
			db.session.commit()
		except:
			db.session.rollback()
		finally:
			db.session.close()

	def unset_user(self):
		institution = self.get_institution(self.id)
		institution.user_id = None

		try:
			db.session.commit()
		except:
			db.session.rollback()
		finally:
			db.session.close()

		return True

	# se normalizan los strings y luego se comparan
	def validate_exist_per_client(self, name, client):

		institutions_per_client = Institutions.query.filter_by(client_id=client).all()

		for institution in institutions_per_client:

			institution_db = re.sub(
			r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
			normalize( "NFD", str(institution.name)), 0, re.I).lower()

			institution_parameter = re.sub(
			r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
			normalize( "NFD", str(name)), 0, re.I).lower()
			if str(institution_db) == str(institution_parameter):
				return True
		else:
			return False

	def validate_by_name(self, name):

		institutions = Institutions.query.filter(Institutions.active == True).all()

		for institution in institutions:

			institution_db = unidecode(str(institution.name)).lower()
			institution_parameter = unidecode(str(name)).lower()

			if str(institution_db) == str(institution_parameter):
				return institution
		else:
			return False

# tabla de contacto local de los establecimientos

class LocalContact(db.Model):
	__tablename__ = 'admin_local_contact'
	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=True)
	phone = Column(String(100), nullable=True)
	email = Column(String(100), nullable=True)
	institution_id = Column(Integer, ForeignKey('admin_institutions.id'))
	institution = db.relationship('Institutions', backref=db.backref(
		'localcontact_institution', lazy='dynamic'))
	active = Column(Boolean, default=True)

	def __repr__(self):
		return self.id

	@staticmethod
	def get_by_id(id):
		return LocalContact.query.get(id)

	def update(self, name, phone, email):
		self.name = name
		self.phone = phone
		self.email = email

		try:
			db.session.commit()
		except:
			db.session.rollback()

	def deactivate(self):
		self.active = False

		try:
			log = LogLocalContact()
			log.action = "deactivate"
			log.local_contact_id = self.id
			log.user_id = current_user.id
			log.setLog()
			db.session.commit()
		except:
			db.session.rollback()
	
	def activate(self):
		self.active = True

		try:
			log = LogLocalContact()
			log.action = "activate"
			log.local_contact_id = self.id
			log.user_id = current_user.id
			log.setLog()
			db.session.commit()
		except:
			db.session.rollback()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
		return self.id

# tabla admin_campaigns

class Campaigns(db.Model):
	__tablename__ = 'admin_campaigns'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=True, unique=True)
	period = Column(String(10), nullable=True)
	client_id = Column(Integer, ForeignKey('admin_clients.id'))
	client = db.relationship('Clients', backref=db.backref(
		'admin_campaigns', lazy='dynamic'))
	active = Column(Boolean, default=True)
	created = Column(DateTime, nullable=True, default=datetime.now())

	def __repr__(self):
		return self.name

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def last_id(self):
		obj = Campaigns.query.order_by(-Campaigns.id).first()
		return obj.id

	def exist(self, campaign):
		exists = db.session.query(db.exists().where(
			Campaigns.name == str(campaign))).scalar()
		return exists

	def finish_campaign(self):
		self.active = False
		try:
			db.session.commit()
		except:
			db.session.rollback()
		finally:
			db.session.close()
		return True

# tabla n:m admin_institutions_campaigns

class InstitutionsCampaigns(db.Model):
	__tablename__ = 'admin_institutions_campaigns'
	id = Column(Integer, primary_key=True)
	institution_id = Column(Integer, ForeignKey('admin_institutions.id'))
	institution = db.relationship('Institutions', backref=db.backref(
		'admin_usadmin_institution', lazy='dynamic'))
	campaign_id = Column(Integer, ForeignKey('admin_campaigns.id'), nullable=True)
	campaign = db.relationship('Campaigns', backref=db.backref(
		'admin_institutionscampaign_campaigns', lazy='dynamic'))
	log_institution_status = db.relationship(
		'LogInstitutionsStatus', backref='institution_campaign', lazy='dynamic')
	local_contact_id = Column(Integer, ForeignKey(
		'admin_local_contact.id'), nullable=True)
	local_contact = db.relationship(
		'LocalContact', backref=db.backref('institutionscampaigns_localcontact', lazy='dynamic'))

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	def get_by_id(self, id):
		return InstitutionsCampaigns.query.get(id)

	def set_local_contact(self, local_contact_id):
		self.local_contact_id = local_contact_id
		try:
			db.session.commit()
		except:
			db.session.rollback()
		finally:
			db.session.close()

# tabla usuarios

class Users(db.Model, UserMixin):
	__tablename__ = 'admin_users'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	lastname = Column(String(80), nullable=False)
	username = Column(String(80), unique=True, nullable=False)
	email = Column(String(80), nullable=True)
	password = Column(String(128), nullable=False)
	category_id = Column(Integer, ForeignKey('admin_users_category.id'))
	category = db.relationship('UsersCategory', backref=db.backref(
		'admin_users_category', lazy='dynamic'))
	is_admin = Column(Boolean, default=False)

	def __repr__(self):
		return f'{self.name} {self.lastname}'

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def update(self):
		user = self.get_by_username(self.username)
		user.username = self.username
		user.name = self.name
		user.lastname = self.lastname
		user.email = self.email
		user.is_admin = self.is_admin
		user.category = self.category
		try:
			db.session.commit()
		except:
			db.session.rollback()
		finally:
			db.session.close()

	def update_password(self):
		user = self.get_by_id(self.id)
		user.password = self.password
		db.session.commit()

	@staticmethod
	def get_by_id(id):
		return Users.query.get(id)

	@staticmethod
	def get_by_username(username):
		return Users.query.filter_by(username=username).first()

	def get_agentes_mda_back(self):
		#result = db.session.query(Users).filter(Users.id.in_((1))).all()
		result = Users.query.filter_by(category_id=1)
		return result
	
	def get_directors(self):
		result = Users.query.filter_by(category_id=4).all()
		return result

class UsersCategory(db.Model):
	__tablename__ = 'admin_users_category'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	alias = Column(String(80), nullable=False)

	def __repr__(self):
		return self.alias

# tabla: admin_link_types
# descripción: registro de tipos de enlaces

class LinkTypes(db.Model):
	__tablename__ = 'admin_link_types'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)

	def __repr__(self):
		return self.name

	def save(self):
		if not self.id:
			db.session.add(self)
			db.session.commit()

	@staticmethod
	def get_by_name(name):
		return LinkTypes.query.filter_by(name=name).first()

# tabla: admin_connection_types
# descripción: registro de tipos de conexiones

class ConnectionTypes(db.Model):
	__tablename__ = 'admin_connection_types'
	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)

	def __repr__(self):
		return self.name

	def save(self):
		if not self.id:
			db.session.add(self)
			db.session.commit()

	@staticmethod
	def get_by_name(name):
		return ConnectionTypes.query.filter_by(name=name).first()


# tabla: admin_links
# descripción: registro de enlaces

class Links(db.Model):
	__tablename__ = 'admin_links'
	id = Column(Integer, primary_key=True)
	service_code = Column(String(80), nullable=True)
	ip_direction = Column(String(80), nullable=True)

	link_type_id = Column(Integer, ForeignKey('admin_link_types.id'))
	link_type = db.relationship(
		'LinkTypes', backref=db.backref('admin_link_types', lazy='dynamic'))

	connection_type_id = Column(Integer, ForeignKey('admin_connection_types.id'))
	connection_type = db.relationship('ConnectionTypes', backref=db.backref(
		'admin_connection_types', lazy='dynamic'))

	institution_id = Column(Integer, ForeignKey(
		'admin_institutions.id'), nullable=True)
	institutions = db.relationship('Institutions', backref=db.backref(
		'admin_links_institutions', lazy='dynamic'))

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def get_by_id(self, id):
		return Links.query.get(id)

	def delete(self):
		db.session.delete(self)
		db.session.commit()
		
	# el código de servicio debe ser único
	def service_code_exist(service_code):
		l = Links.query.filter_by(service_code=service_code).first()
		if l is None:
			return False
		else:
			return True

class SendMails(db.Model):
	__tablename__ = 'admin_send_mails'
	id = Column(Integer, primary_key=True)
	description = Column(String(100), nullable=False)

class SendMailsCC(db.Model):
	__tablename__ = 'admin_send_mails_cc'
	id = Column(Integer, primary_key=True)
	mail = Column(String(150), nullable=True)
	send_mail_id = Column(Integer, ForeignKey('admin_send_mails.id'), nullable=True)
	send_mail = db.relationship('SendMails', backref=db.backref('mails_send_mailscc', lazy='dynamic'))
	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('admin_sendmailscc_users', lazy='dynamic'))

	def __repr__(self):
		if self.mail is not None:
			return self.mail
		if self.user_id is not None:
			return self.user.email

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	def delete(self):
		db.session.delete(self)
		db.session.commit()

class SendMailsFrom(db.Model):
	__tablename__ = 'admin_send_mails_from'
	id = Column(Integer, primary_key=True)
	mail = Column(String(150), nullable=True)
	send_mail_id = Column(Integer, ForeignKey('admin_send_mails.id'), nullable=True)
	send_mail = db.relationship('SendMails', backref=db.backref('mails_send_mailsfrom', lazy='dynamic'))
	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('admin_sendmailsfrom_users', lazy='dynamic'))

	def __repr__(self):
		if self.mail is not None:
			return self.mail
		if self.user_id is not None:
			return self.user.email

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	def delete(self):
		db.session.delete(self)
		db.session.commit()

#tabla de grupos de correos
class GroupsMails(db.Model):
	__tablename__ = 'admin_groups_mails'
	id = Column(Integer, primary_key=True)
	name = Column(String(200), nullable=False)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

# relación grupo_correo 1:n clientes
class ClientsGroupsMails(db.Model):
	__tablename__ = 'admin_clients_groups_mails'
	id = Column(Integer, primary_key=True)

	client_id = Column(Integer, ForeignKey('admin_clients.id'), unique=True, nullable=False)
	clients = db.relationship('Clients', backref=db.backref(
		'admin_clientsgroupsmails_clients', lazy='dynamic'
	))
	groupmail_id = Column(Integer, ForeignKey('admin_groups_mails.id'), nullable=False)
	groupmail = db.relationship('GroupsMails', backref=db.backref(
		'admin_clientsgroupsmails_groupsmails', lazy='dynamic'
	))

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

class ItemGroupsMails(db.Model):
	__tablename__ = 'admin_item_groups_mails'
	id = Column(Integer, primary_key=True)

	name = Column(String(200), nullable=True)
	mail = Column(String(150), nullable=False)

	group_mail_id = Column(Integer, ForeignKey('admin_groups_mails.id'))
	group = db.relationship('GroupsMails', backref=db.backref(
		'admin_itemgroupsmails_groupsmails', lazy='dynamic'
	))

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

#relación n:n entre group_mails y send_mails
# aquí se relaciona un grupo de correos a una tarea programada
# type: 0 = FROM || 1 = CC
class GroupMailsSendMails(db.Model):
	__tablename__ = 'admin_groupmails_sendmails'
	id = Column(Integer, primary_key=True)

	groupmail_id = Column(Integer, ForeignKey('admin_groups_mails.id'), nullable=False, unique=False)
	group = db.relationship('GroupsMails', backref=db.backref(
		'admin_groupmails_sendmails__admin_group_mails', lazy = 'dynamic'
	))

	send_mail_id = Column(Integer, ForeignKey('admin_send_mails.id'), nullable=True, unique=False)
	send_mail = db.relationship('SendMails', backref=db.backref('admin_groupmails_sendmails__admin_send_mails', lazy='dynamic'))

	type = Column(SmallInteger, nullable=False)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	
	def delete(self):
		db.session.delete(self)
		db.session.commit()