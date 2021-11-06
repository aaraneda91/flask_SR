from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Time, String, Boolean, exists, engine, DateTime
import re
from unicodedata import normalize
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# modelos exclusivo para registro de historial


class LogInstitutionsStatus(db.Model):
	__tablename__ = 'log_institutions_states'
	id = Column(Integer, primary_key=True)

	institution__campaing_id = Column(Integer, ForeignKey(
		'admin_institutions_campaigns.id'), nullable=False)
	institutioncampaign = db.relationship('InstitutionsCampaigns', backref=db.backref(
		'logs_institutions_campaigns', lazy='dynamic'))

	from_status_id = Column(Integer, ForeignKey(
		'admin_status_institutions.id'), nullable=True)
	from_status = db.relationship(
		'InstitutionsStatus', foreign_keys=[from_status_id])

	to_status_id = Column(Integer, ForeignKey(
		'admin_status_institutions.id'), nullable=True)
	to_status = db.relationship(
		'InstitutionsStatus', foreign_keys=[to_status_id])

	ticket_ar = Column(String(100), nullable=True)

	date_coord = Column(Date, nullable=True)
	time_coord = Column(Time, nullable=True)

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users', foreign_keys=[user_id])

	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return self.id

	def setLog(self):
		db.session.add(self)
		db.session.commit()

	def return_days(self, days):
		status_days = days
		today = datetime.today()
		today = today + timedelta(days = 1)
		remaining_days = (today-status_days).days
		return remaining_days


class LogLogin(db.Model):
	__tablename__ = 'log_login'
	id = Column(Integer, primary_key=True)

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
	user = db.relationship('Users', foreign_keys=[user_id])

	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def setLog(self):
		db.session.add(self)
		db.session.commit()

class LogCampaignStatus(db.Model):
	__tablename__ = 'log_campaigns_status'
	id = Column(Integer, primary_key = True)

	campaign_id = Column(Integer, ForeignKey('admin_campaigns.id'), nullable=False)
	campaign = db.relationship('Campaigns', foreign_keys=[campaign_id])

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
	user = db.relationship('Users', foreign_keys=[user_id])

	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def setLog(self):
		db.session.add(self)
		db.session.commit()

class LogCommunesName(db.Model):
	__tablename__ = 'log_communes_name'
	id = Column(Integer, primary_key = True)

	name_before = Column(String(150), nullable=False)
	name_after = Column(String(150), nullable=False)

	commune_id = Column(Integer, ForeignKey('admin_communes.id'), nullable=False)
	commune = db.relationship('Communes', backref=db.backref('logs_communes', lazy='dynamic'))

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('logs_users', lazy='dynamic'))

	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def setLog(self):
		db.session.add(self)
		db.session.commit()

class LogLocalContact(db.Model):
	__tablename__ = 'log_local_contact'
	id = Column(Integer, primary_key = True)

	action = Column(String(150), nullable=False)

	local_contact_id = Column(Integer, ForeignKey('admin_local_contact.id'), nullable=False)
	local_contact = db.relationship('LocalContact', backref=db.backref('logs_local_contact', lazy='dynamic'))

	user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=True)
	user = db.relationship('Users',backref=db.backref('local_contact_logs_users', lazy='dynamic'))

	created = Column(DateTime, nullable=False, default=datetime.utcnow)

	def setLog(self):
		db.session.add(self)
		db.session.commit()