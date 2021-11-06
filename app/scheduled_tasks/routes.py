from datetime import datetime
from flask.helpers import url_for
from flask.templating import render_template
from flask_mail import Message
from sqlalchemy.sql.operators import concat_op
from . import tasks_bp

from app.admin.models import Campaigns, ClientsDirectors, GroupMailsSendMails, Institutions, InstitutionsCampaigns, LocalContact, SendMailsCC, SendMailsFrom, Users, GroupsMails, ClientsGroupsMails, ItemGroupsMails

from app import mail, app
from flask_mail import Message
from sqlalchemy import or_
import locale

locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))

def get_contacts_cc(send_mail_id):
   contacts_cc = []
   #contactos anónimos
   data_row_cc_anon = SendMailsCC.query.filter(SendMailsCC.send_mail_id == send_mail_id, SendMailsCC.user_id == None).all()
   for data in data_row_cc_anon:
      mail_cc = str(data.mail)
      contacts_cc.append(mail_cc)

   #contactos registrados
   contacts_cc_registered = SendMailsCC.query.filter(SendMailsCC.send_mail_id == send_mail_id, SendMailsCC.user_id != None).join(Users).all()
   for data in contacts_cc_registered:
      mail_cc = str(data.user.email)
      contacts_cc.append(mail_cc)
   return contacts_cc

def get_contacts_from(send_mail_id):
   contacts_from = []
   #contactos anónimos
   data_row_from_anon = SendMailsFrom.query.filter(SendMailsFrom.send_mail_id == send_mail_id, SendMailsFrom.user_id == None).all()
   for data in data_row_from_anon:
      mail_from = str(data.mail)
      contacts_from.append(mail_from)

   #contactos registrados
   contacts_from_registered = SendMailsFrom.query.filter(SendMailsFrom.send_mail_id == send_mail_id, SendMailsFrom.user_id != None).join(Users).all()

   for data in contacts_from_registered:
      mail_from = str(data.user.email)
      contacts_from.append(mail_from)
   return contacts_from

def get_contacs_mda():
   contacts_mda = []

   users = Users.query.filter(or_(Users.category_id == 1, Users.category_id == 2, Users.category_id == 5)).all()
   for user in users:
      mail = str(user.email)
      contacts_mda.append(mail)
   return contacts_mda

def get_contacts_in_groups(client_id, sendmail, type):

   data = []

   groups_in_sendmail = GroupMailsSendMails.query.filter(GroupMailsSendMails.send_mail_id == sendmail, GroupMailsSendMails.type == type).all()
   
   for group in groups_in_sendmail:
      groupclient = ClientsGroupsMails.query.filter(ClientsGroupsMails.groupmail_id == group.groupmail_id, ClientsGroupsMails.client_id == client_id).first()

      if groupclient is not None:
         contacts = ItemGroupsMails.query.join(GroupsMails).join(ClientsGroupsMails).filter(ClientsGroupsMails.client_id == client_id).all()

         for contact in contacts:
            data.append(str(contact.mail))

   return data

#retorna fecha formato "1 de enero de 2021"
def date_format(date):
   date_day = date.strftime("%d")
   date_month = date.strftime("%B")
   date_year = date.strftime("%Y")
   return str(date_day+' de '+date_month+' de '+date_year)

# retorna hora formato "24:00"
def time_format(time):
   time_hour = time.strftime("%H")
   time_minutes = time.strftime("%M")
   return str(time_hour+':'+time_minutes)

# Tarea que cambia los establecimientos desde Coordinados a Por ejecutar y envía correo informando a los contactos locales asignados.
# cada viernes a las 20:00
@app.cli.command("task-01")
def task_01():

   contact_cc = []
   contact_from = []
   institutions_updated = []

   obj = InstitutionsCampaigns.query.join(Campaigns).join(Institutions).join(LocalContact).filter(Campaigns.active == True, Institutions.active == True, Institutions.status_id == 8).all()

   contact_cc = get_contacts_cc(send_mail_id=1)
   contact_from = get_contacts_from(send_mail_id=1)
   user_system = Users.query.filter(Users.username == 'system').first()
   
   for row in obj:

      date_coord = date_format(row.institution.date_coord)
      time_coord = time_format(row.institution.time_coord)

      #correo al director de servicios
      director = ClientsDirectors.query.filter(ClientsDirectors.clients_id == row.institution.client_id).first()

      groups_cc = get_contacts_in_groups(row.institution.client_id, 1, 1)
      groups_from = get_contacts_in_groups(row.institution.client_id, 1, 0)

      msg = Message("Programación de Prueba de Respaldo GGC",
      #recipients=[row.local_contact.email]+contact_from+groups_from, cc = [director.directors.email]+contact_cc+groups_cc)
      recipients=[row.local_contact.email]+contact_from+groups_from, cc = contact_cc+groups_cc)
      msg.html = render_template(
         'task_01.html',
         client_name = row.institution.client.name,
         institution_address = row.institution.address,
         institution_name = row.institution.name,
         date_coord = date_coord,
         time_coord = time_coord,
         local_contact_name = row.local_contact.name,
         local_contact_phone = row.local_contact.phone
         )

      mail.send(msg)
      i = Institutions()
      i.id = row.institution.id
      i.status_id = 9
      i.set_status(campaign_institution_id=row.id, current_user_id=user_system.id)
      institutions_updated.append(row.institution.name)

# Tarea que avisa las pruebas Por ejecutar y En ejecución para el día actual a cada uno de los contactos locales asignados.
# Todos los días a las 8 am
@app.cli.command("task-02")
def task_02():

   contact_cc = []
   contact_from = []
   array_institutions = []

   todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

   obj = InstitutionsCampaigns.query.join(Campaigns).join(Institutions).filter(Campaigns.active == True, Institutions.active == True, Institutions.date_coord == todays_datetime, or_(Institutions.status_id == 9, Institutions.status_id == 15)).all()

   contact_cc = get_contacts_cc(send_mail_id=2)
   contact_from = get_contacts_from(send_mail_id=2)
      
   for row in obj:

      date_coord = date_format(row.institution.date_coord)
      time_coord = time_format(row.institution.time_coord)

      groups_cc = get_contacts_in_groups(row.institution.client_id, 2, 1)
      groups_from = get_contacts_in_groups(row.institution.client_id, 2, 0)

      #correo al director de servicios
      director = ClientsDirectors.query.filter(ClientsDirectors.clients_id == row.institution.client_id).first()
      
      msg = Message("Aviso Prueba de Respaldo Coordinada GGC",
      #recipients=[row.local_contact.email]+contact_from, cc = [director.directors.email]+contact_cc)
      recipients=[row.local_contact.email]+contact_from+groups_from, cc = contact_cc+groups_cc)
      msg.html = render_template(
         'task_02.html',
         client_name = row.institution.client.name,
         institution_name = row.institution.name,
         date_coord = date_coord,
         time_coord = time_coord,
         local_contact_name = row.local_contact.name
         )
      mail.send(msg)
      array_institutions.append(row.institution.name)

# Tarea que avisa las pruebas coordenadas para el día de hoy a los usuarios MDA.
@app.cli.command("task-03")
def task_03():

   array_institutions = []

   todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

   obj = InstitutionsCampaigns.query.join(Campaigns).join(Institutions).filter(Campaigns.active == True, Institutions.active == True, Institutions.date_coord == todays_datetime,or_(Institutions.status_id == 9, Institutions.status_id == 15)).order_by(Institutions.time_coord).all()

   contact_cc = get_contacts_cc(send_mail_id=3)
   contact_from = get_contacts_from(send_mail_id=3)

   for row in obj:
      array_institutions.append(row.institution)

   #fecha de hoy
   str_today = date_format(todays_datetime)

   if len(array_institutions) > 0:
      msg = Message("Recordatorio Diario Pruebas de Respaldos GGC",
      recipients=contact_from, cc = contact_cc)
      msg.html = render_template(
            'task_03.html',
            institutions = array_institutions,
            str_today = str_today
            )
      mail.send(msg)
   else:
      pass