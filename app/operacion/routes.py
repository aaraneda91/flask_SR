from flask import json, render_template, redirect, request, url_for, send_file, jsonify, request, send_from_directory, abort
from flask_login import current_user
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import count
from . import operacion_bp
from app.admin.models import ClientsDirectors, Institutions, Users, Campaigns, InstitutionsStatus, InstitutionsCampaigns, InstitutionsCampaignsComments, InstitutionsCampaignsFiles, LocalContact
from docxtpl import DocxTemplate
from datetime import datetime
import io, pytz
from app.config.const_logger import STATUS_INSTITUTIONS
import os
from app import app
from werkzeug.utils import secure_filename
from uuid import uuid4

@operacion_bp.route("/operacion/upload", methods=['POST'])
def upload_file():
	institution_id = request.form.get('institution_id')
	uploaded_file = request.files['file']

	if not uploaded_file:
		return jsonify(
			status = False,
			message = "Debe adjuntar un archivo"
		)

	if not institution_id:
		return jsonify(
			status = False,
			message = "No se ha indicado la institucion correspondiente"
		)

	filename = secure_filename(uploaded_file.filename)

	institution = Institutions.get_institution(institution_id)
	institution_campaign = InstitutionsCampaigns.query.join(Institutions).filter_by(id = institution.id).first()
	
	upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(institution_campaign.id))

	if not os.path.exists(upload_file_path):
		os.makedirs(upload_file_path)
	
	unique_filename = uuid4().__str__()
	uploaded_file.save(os.path.join(upload_file_path, unique_filename))

	add_file = InstitutionsCampaignsFiles(institution_campaign_id = institution_campaign.id, user_id = current_user.id, status_id = institution.status_id, filename = filename, unique_filename = unique_filename)
	add_file.save()

	return jsonify(
		status = True,
		message = "Archivo cargado"
	)

@operacion_bp.route("/operacion/get_files/current_period", methods=['POST'])
def get_files_current_period():
	institution_id = request.form.get('institution_id')

	if not institution_id:
		return jsonify(
			status = False,
			message = "No se ha indicado la institucion correspondiente"
		)

	tz = pytz.timezone('America/Santiago')
	utc = pytz.timezone('UTC')

	institution = Institutions.get_institution(institution_id)
	institution_campaign = InstitutionsCampaigns.query.join(Institutions).filter_by(id = institution.id).first()
	campaign = Campaigns.query.filter_by(id = institution_campaign.campaign.id).first()

	institutions_campaigns_files = InstitutionsCampaignsFiles.query.filter_by(institution_campaign_id = institution_campaign.id).join(InstitutionsCampaigns).join(Campaigns).filter_by(period = campaign.period).join(InstitutionsStatus).order_by(-InstitutionsCampaignsFiles.id).all()

	if not institutions_campaigns_files:
		return jsonify(
			status = False,
			message = "No existen archivos"
		)
	else:

		data = {}
		for idx, d in enumerate(institutions_campaigns_files):
			data[idx] = {'id' : d.id, 'period': d.institution_campaign.campaign.period, 'filename' : d.filename, 'unique_filename' : d.unique_filename, 'user' : d.user.name + ' ' + d.user.lastname, 'date' : utc.localize(d.created).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"), 'status' : d.status.alias}

		return jsonify(
			status = True,
			message = "Listado de Archivos",
			files = data
		)


@operacion_bp.route("/operacion/get_files/previous_period", methods=['POST'])
def get_files_previous_preriod():
	institution_id = request.form.get('institution_id')

	if not institution_id:
		return jsonify(
			status = False,
			message = "No se ha indicado la institucion correspondiente"
		)

	tz = pytz.timezone('America/Santiago')
	utc = pytz.timezone('UTC')

	institution = Institutions.get_institution(institution_id)
	institution_campaign = InstitutionsCampaigns.query.join(Institutions).filter_by(id = institution.id).first()
	campaign = Campaigns.query.filter_by(id = institution_campaign.campaign.id).first()
	previous_period = str(int(campaign.period) - int(1))
	institutions_campaigns_files = InstitutionsCampaignsFiles.query.filter_by(institution_campaign_id = institution_campaign.id).join(InstitutionsCampaigns).join(Campaigns).filter_by(period = previous_period).join(InstitutionsStatus).order_by(-InstitutionsCampaignsFiles.id).all()

	if not institutions_campaigns_files:
		return jsonify(
			status = False,
			message = "No existen archivos"
		)
	else:

		data = {}
		for idx, d in enumerate(institutions_campaigns_files):
			data[idx] = {'id' : d.id, 'period': d.institution_campaign.campaign.period, 'filename' : d.filename, 'unique_filename' : d.unique_filename, 'user' : d.user.name + ' ' + d.user.lastname, 'date' : utc.localize(d.created).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"), 'status' : d.status.alias}

		return jsonify(
			status = True,
			message = "Listado de Archivos",
			files = data
		)

@operacion_bp.route("/operacion/download/<string:file_uuid>", methods=['GET'])
def download_files(file_uuid = None):
	if not file_uuid:
		abort(404)
	else:
		file = InstitutionsCampaignsFiles.get_by_unique_filename(file_uuid)
		if not file:
			abort(404)
		else:
			path = os.path.join(app.config['UPLOAD_FOLDER'], str(file.institution_campaign_id), str(file.unique_filename))
			return send_file(path, attachment_filename = file.filename, as_attachment=True)

@operacion_bp.route("/operacion/delete_file", methods=['POST'])
def delete_file(file_uuid = None):
	if not current_user.is_admin:
		return jsonify(
			status = False,
			message = "No tiene permisos para realizar la accion seleccionada"
		)
	
	file_uuid = request.form.get('file_uuid')
	if not file_uuid:
		return jsonify(
			status = False,
			message = "Debe indicar archivo a eliminar"
		)
	else:
		file = InstitutionsCampaignsFiles.get_by_unique_filename(file_uuid)
		if not file:
			return jsonify(
				status = False,
				message = "Archivo no existe"
			)
		else:
			path = os.path.join(app.config['UPLOAD_FOLDER'], str(file.institution_campaign_id), str(file.unique_filename))
			file.delete()
			
			if os.path.isfile(path):
				os.remove(path)
				return jsonify(
					status = True,
					message = "Archivo eliminado"
				)
			else:
				return jsonify(
					status = False,
					message = "Archivo no existe en el sistema, se elimina registro"
				)

@operacion_bp.route("/operacion/add_observation", methods=['POST'])
def add_observation():
	comment = request.form.get('observacion')
	institution_id = request.form.get('institution_id')

	if not comment:
		return jsonify(
			status = False,
			message = "Debe indicar una observacion"
		)

	if not institution_id:
		return jsonify(
			status = False,
			message = "No se ha indicado la institucion correspondiente"
		)

	institution = Institutions.get_institution(institution_id)
	institution_campaign = InstitutionsCampaigns.query.join(Institutions).filter_by(id = institution.id).first()

	add_comment = InstitutionsCampaignsComments(institution_campaign_id = institution_campaign.id, user_id = current_user.id, status_id = institution.status_id, comment = comment)
	add_comment.save()

	return jsonify(
		status = True,
		message = "Observacion creada"
	)

@operacion_bp.route("/operacion/get_observations", methods=['POST'])
def get_observation():
	institution_id = request.form.get('institution_id')

	if not institution_id:
		return jsonify(
			status = False,
			message = "No se ha indicado la institucion correspondiente"
		)

	tz = pytz.timezone('America/Santiago')
	utc = pytz.timezone('UTC')

	institution = Institutions.get_institution(institution_id)
	institution_campaign = InstitutionsCampaigns.query.join(Institutions).filter_by(id = institution.id).first()

	institutions_campaigns_comments = InstitutionsCampaignsComments.query.filter_by(institution_campaign_id = institution_campaign.id).join(InstitutionsStatus).order_by(-InstitutionsCampaignsComments.id).all()
	
	if not institutions_campaigns_comments:
		return jsonify(
			status = False,
			message = "No existen observaciones"
		)
	else:
		data = {}
		for idx, d in enumerate(institutions_campaigns_comments):
			data[idx] = {'id' : d.id, 'comment' : d.comment, 'user' : d.user.name + ' ' + d.user.lastname, 'date' : utc.localize(d.created).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"), 'status' : d.status.alias}

		return jsonify(
			status = True,
			message = "Listado de observaciones",
			observations = data
		)

@operacion_bp.route("/operacion/flujo/")
def phases():
	title = "Flujo - Sistema de respaldos"
	return render_template("flujo.html", title = title)

# etapa Gestión

@operacion_bp.route("/operacion/gestion", methods=['GET','POST'])
def phase1():

	institutions = Institutions()
	institutions = institutions.get_gestion()

	data_directors = ClientsDirectors.query.all()
	
	return render_template(
		"gestion.html", 
		phase1 = "active",
		title = "Gestión - Sistema de respaldos",
		campaigns = institutions,
		directors = data_directors)

@operacion_bp.route("/operacion/cambiar_estado/<int:institution_id>/<int:new_status>/<int:campaign_institution_id>", methods=['GET'])
def change_status(institution_id, new_status,campaign_institution_id):
	# se cambia de estado
	if request.method == 'GET':
		id = institution_id
		status = new_status
		institutions = Institutions()
		institutions.id = id
		institutions.status_id = status
		institutions.unset_user()
		prev_status = institutions.set_status(campaign_institution_id = campaign_institution_id)

		if status in (STATUS_INSTITUTIONS['POR_GESTIONAR'], STATUS_INSTITUTIONS['ESCALADO'], STATUS_INSTITUTIONS['INCIDENTE'], STATUS_INSTITUTIONS['PRUEBA_FALLIDA'],STATUS_INSTITUTIONS['SIN_REVISAR'], STATUS_INSTITUTIONS['EN_REVISION']):
			institutions.set_coordination(date = None, time = None)

		# se retorna a la vista del estado previo
		if prev_status in (STATUS_INSTITUTIONS['POR_GESTIONAR'], STATUS_INSTITUTIONS['ESCALADO'], STATUS_INSTITUTIONS['INCIDENTE'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['PRUEBA_FALLIDA']):
			return redirect(url_for('operacion.phase1'))

		if prev_status in (STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['COORDINADO']):
			return redirect(url_for('operacion.phase3'))
		
		return redirect(url_for('operacion.phase1'))
	
	return redirect(url_for('operacion.phase1'))

# esta ruta es sólo para cambiar de estado a exitoso, exitiso con observaciones, cancelada y fallida a través de POST
@operacion_bp.route("/operacion/cambiar_estado_post", methods=['POST'])
def change_status_post():

	if request.method == 'POST':
		id_user = current_user.id
		id = request.form.get('institution')
		status = request.form.get('status')
		ticket_ar = request.form.get('ticket_ar')
		institution_campaign = request.form.get('institution_campaign') 
		institutions = Institutions()
		institutions.id = id
		institutions.status_id = status

		if ticket_ar:
			add_comment = InstitutionsCampaignsComments(institution_campaign_id = institution_campaign, user_id = current_user.id, status_id = status, comment = f'Se registra ticket {ticket_ar}')
			add_comment.save()

		prev_status = institutions.set_status(campaign_institution_id=institution_campaign, ticket_ar=ticket_ar)
		institutions.unset_user()
		if status in ('11','12'):
			print("borrar datos coordinacion")
			institutions.set_coordination(date = None, time = None)

		# cambio de estado a Exitoso con observaciones
		# se registra observación obligatoria

		if request.form.get("required_comment"):
			comment = request.form.get("required_comment")

			institution = Institutions.get_institution(id)

			add_comment = InstitutionsCampaignsComments(institution_campaign_id = institution_campaign, user_id = id_user, status_id = status, comment = comment)
			add_comment.save()

		if prev_status in (STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION']):
			return redirect(url_for('operacion.phase4'))

		if prev_status in (STATUS_INSTITUTIONS['SIN_REVISAR'], STATUS_INSTITUTIONS['EN_REVISION']):
			return redirect(url_for('operacion.phase2'))

		if prev_status in (STATUS_INSTITUTIONS['PRUEBA_EXITOSA'], STATUS_INSTITUTIONS['EXITOSO_OBSERVACION']):
			return redirect(url_for('operacion.phase5'))

	return redirect(url_for('operacion.phase4'))


def datetimefilter(value):
	tz = pytz.timezone('America/Santiago') # timezone you want to convert to from UTC
	utc = pytz.timezone('UTC')  
	value = utc.localize(value)
	local_dt = value.astimezone(tz)
	final_value= local_dt.strftime("%Y-%m-%d")+' ('+local_dt.strftime("%H:%M")+')'

	return final_value
app.jinja_env.filters['datetimefilter'] = datetimefilter

# Revisión

@operacion_bp.route("/operacion/revision")
def phase2():

	institutions = Institutions()
	institutions = institutions.get_revision()

	users = Users()
	users = users.get_agentes_mda_back()

	data_directors = ClientsDirectors.query.all()

	return render_template(
		"revision.html", 
		revision = True,
		title = "Revisión - Sistema de respaldos", 
		phase2 = "active",
		campaigns = institutions,
		users = users,
		directors = data_directors
		)

# este método es utilizado para asignar usuarios a establecimientos que están en Revisión y en Ejecución
@operacion_bp.route("/operacion/revision/asignar_usuario", methods=["POST"])
def assign_user():

	if request.method == 'POST':

		user_id = request.form.get('user')
		institution_id = request.form.get('institution')
		institution_campaign = request.form.get('institution_campaign')

		institutions = Institutions()
		institution = institutions.get_by_id(institution_id)
		institution.user_id = user_id

		if request.form.get('from_status') == '2':

			institution.save()

			tmp_institutions = Institutions()
			tmp_institutions.id = institution_id
			tmp_institutions.status_id = 3
			tmp_institutions.set_status(campaign_institution_id=institution_campaign)

			return redirect(url_for('operacion.phase2'))

		if request.form.get('from_status') in ('9','15'):

			institution.save()

			tmp_institutions = Institutions()
			tmp_institutions.id = institution_id
			tmp_institutions.status_id = 15
			tmp_institutions.set_status(campaign_institution_id=institution_campaign)

			return redirect(url_for('operacion.phase4'))
		else:
			institution.save()

	return redirect(url_for('operacion.phase2'))

# FASE DE COORDINACIÓN

@operacion_bp.route("/operacion/coordinacion/<string:msg>/<int:id>", methods=["POST"])
@operacion_bp.route("/operacion/coordinacion")
def phase3(msg=None, id=None):

	institutions = Institutions()
	institutions = institutions.get_coordinacion()

	if request.method == "POST":

		if msg == "edit_contact":
			inst = Institutions.query.filter_by(id=id).first()
			msg = "Se ha editado correctamente el establecimiento <b>"+str(inst.name)+"</b>. <a href='#' data-toggle='modal' data-target='#modalLocalContact_"+str(inst.id)+"'>Ver contactos</a>"

	data_directors = ClientsDirectors.query.all()

	return render_template(
		"coordinacion.html", 
		phase3 = "active",
		title = "Coordinación - Sistema de respaldos", 
		campaigns = institutions,
		msg = msg,
		directors = data_directors)

@operacion_bp.route("/operacion/coordinar/<int:institution_id>/<int:institution_campaign_id>/", methods=["POST"])
def coordinate(institution_id,institution_campaign_id):

	if request.method == 'POST':

		date = request.form.get('date')
		time = request.form.get('time')
		
		institutions = Institutions()
		institutions.id = institution_id

		check_coord = institutions.get_institution(institutions.id)
		check_coord_prev_status = check_coord.status.id

		if(check_coord.date_coord is None and check_coord.time_coord is None):
			
			institutions.set_coordination(date = date, time = time)
			institutions.status_id = 8
			prev_status = institutions.set_status(date_coord=date, time_coord=time,campaign_institution_id=institution_campaign_id, current_user_id=current_user.id)

			add_comment = InstitutionsCampaignsComments(institution_campaign_id = institution_campaign_id, user_id = current_user.id, status_id = prev_status, comment = f'Se realiza coordinacion con fecha {date} a las {time}')
			add_comment.save()
			
			if prev_status in (STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['COORDINADO']):
				return redirect(url_for('operacion.phase3'))
			elif prev_status in (STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION']):
				return redirect(url_for('operacion.phase4'))
		else:
			institutions.set_coordination(date = date, time = time)
			add_comment = InstitutionsCampaignsComments(institution_campaign_id = institution_campaign_id, user_id = current_user.id, status_id = check_coord_prev_status, comment = f'Se realiza coordinacion con fecha {date} a las {time}')
			add_comment.save()

			if check_coord_prev_status in (STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['COORDINADO']):
				return redirect(url_for('operacion.phase3'))
			elif check_coord_prev_status in (STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION']):
				return redirect(url_for('operacion.phase4'))
	else:
		abort(404)

# FASE DE EJECUCIÓN
@operacion_bp.route("/operacion/ejecucion/<string:msg>/<int:id>", methods=["POST"])
@operacion_bp.route("/operacion/ejecucion")
def phase4(msg=None, id=None):

	title = "Ejecución - Sistema de respaldos"

	institutions = Institutions()
	institutions = institutions.get_ejecucion()

	users = Users()
	users = users.get_agentes_mda_back()

	if request.method == "POST":

		if msg == "edit_contact":
			inst = Institutions.query.filter_by(id=id).first()
			msg = "Se ha editado correctamente el establecimiento <b>"+str(inst.name)+"</b>. <a href='#' data-toggle='modal' data-target='#modalLocalContact_"+str(inst.id)+"'>Ver contactos</a>"

	data_directors = ClientsDirectors.query.all()

	return render_template(
		"ejecucion.html", 
		title = title, 
		phase4 = "active",
		campaigns = institutions,
		directors = data_directors,
		users = users,
		msg = msg)


@operacion_bp.route("/operacion/ejecucion/doc/<int:institution_campaign_id>/", methods=["GET"])
def ejecution_doc(institution_campaign_id):
	campaign = InstitutionsCampaigns()
	campaign = campaign.get_by_id(institution_campaign_id)

	coordinator_name = ''
	coordinator_lastname = ''
	for i in campaign.log_institution_status:
		if i.to_status_id == STATUS_INSTITUTIONS['POR_EJECUTAR']:
			coordinator_name = i.user.name
			coordinator_lastname = i.user.lastname

	institution_contact_name = ''
	if campaign.local_contact:
		institution_contact_name = campaign.local_contact.name

	executor_name = ''
	executor_last_name = ''
	if campaign.institution.user:
		executor_name = campaign.institution.user.name
		executor_last_name = campaign.institution.user.lastname

	doc = DocxTemplate(os.path.join(app.root_path,"static/download/template_ejecution.docx"))
	context = {'establecimiento': campaign.institution.name,
			   'fecha_hoy': datetime.now().strftime("%d-%m-%Y"),
			   'nombre_coordinador': coordinator_name,
			   'apellido_coordinador': coordinator_lastname,
			   'nombre_ejecutor': executor_name,
			   'apellido_ejecutor': executor_last_name,
			   'nombre_contacto_local': institution_contact_name,
			   }

	doc.render(context)
	file_stream = io.BytesIO()
	doc.save(file_stream)
	file_stream.seek(0)
	return send_file(file_stream, as_attachment=True, attachment_filename=campaign.institution.name+'.docx')

# FASE DE TERMINADOS

@operacion_bp.route("/operacion/terminados")
def phase5():

	institutions = Institutions()
	institutions = institutions.get_terminados()

	data_directors = ClientsDirectors.query.all()

	return render_template(
		"terminados.html", 
		title = "Terminados - Sistema de respaldos", 
		phase5 = "active",
		campaigns = institutions,
		directors = data_directors)

@operacion_bp.route('/local_contact/add', methods=['POST'])
def add_contact():
	institution_id = request.form.get('institution_id')

	inst = Institutions.query.get(institution_id)

	local_contact_id = inst.add_contact(request.form.get('name'), request.form.get('phone'), request.form.get('email'))

	if inst.status_id in (STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['COORDINADO'],STATUS_INSTITUTIONS['POR_EJECUTAR'],STATUS_INSTITUTIONS['EN_EJECUCION']):
		institution_campaign = InstitutionsCampaigns.query.get(institution_id)
		print(institution_campaign)

		contacts = LocalContact.query.filter_by(institution_id = institution_id, active = True)
		data = {}
		for idx, d in enumerate(contacts):
			data[idx] = {'id' : d.id, 'name': d.name, 'phone' : d.phone, 'email' : d.email, 'selected' : False }

		return jsonify(
			status = True,
			message = "Listado de Contactos",
			contacts = data
		)
	elif inst.status_id in (STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION']):
		return redirect(url_for('operacion.phase4'))

@operacion_bp.route('/local_contact/set', methods=['POST'])
def set_local_contact():
	local_contact_id = request.form.get('local_contact_id')
	institution_campaign_id = request.form.get('institution_campaign_id')

	institution_campaign = InstitutionsCampaigns.query.get(institution_campaign_id)
	institution_campaign.set_local_contact(local_contact_id)

	institution_id = InstitutionsCampaigns.query.filter_by(id=institution_campaign_id).first()

	return jsonify(
		status = True,
		message = "Contacto Local Fijado",
		institution = institution_id.institution.id,
		institution_name = institution_id.institution.name,
		local_contact_name = institution_id.local_contact.name
	)

@operacion_bp.route('/contact/get', methods=['POST'])
def get_contact():
	local_contact_id = request.form.get('local_contact_id')

	local_contact = LocalContact.query.get(local_contact_id)

	return jsonify(
		status = True,
		message = "Contacto Encontrado",
		contact = {"id" : local_contact.id, "name" : local_contact.name, "phone" : local_contact.phone, "email" : local_contact.email, "active" : local_contact.active}
	)

@operacion_bp.route('/contact/edit', methods=['POST'])
def edit_contact():
	local_contact_id = request.form.get('local_contact_id')

	local_contact = LocalContact.query.get(local_contact_id)
	local_contact.update(request.form.get('name'), request.form.get('phone'), request.form.get('email'))
	
	inst = Institutions.query.get(local_contact.institution_id)

	if inst.status_id in (STATUS_INSTITUTIONS['POR_COORDINAR'], STATUS_INSTITUTIONS['APTO'], STATUS_INSTITUTIONS['PRUEBA_CANCELADA'], STATUS_INSTITUTIONS['COORDINADO']):
		return redirect(url_for('operacion.phase3', msg="edit_contact", id=inst.id), code=307)
	elif inst.status_id in (STATUS_INSTITUTIONS['POR_EJECUTAR'], STATUS_INSTITUTIONS['EN_EJECUCION']):
		return redirect(url_for('operacion.phase4', msg="edit_contact", id=inst.id), code=307)

	return jsonify(
		status = True,
		message = "Contacto Actualizado"
	)

@operacion_bp.route('/contact/deactivate', methods=['POST'])
def deactivate_contact():
	local_contact_id = request.form.get('local_contact_id')

	local_contact = LocalContact.query.get(local_contact_id)
	local_contact.deactivate()

	return jsonify(
		status = True,
		message = "Contacto Desactivado",
		institution_id = local_contact.institution_id,
		institution_name = local_contact.institution.name
	)

# obtener contactos
@operacion_bp.route('/operacion/contacts', methods=['POST'])
def get_contacts():
	institution_campaign_id = request.form.get('institution_campaign_id')
	institution_campaign = InstitutionsCampaigns.query.get(institution_campaign_id)

	contacts = LocalContact.query.filter_by(institution_id = institution_campaign.institution_id, active = True)
	data = {}
	for idx, d in enumerate(contacts):
		data[idx] = {'id' : d.id, 'name': d.name, 'phone' : d.phone, 'email' : d.email, 'selected' : True if d.id == institution_campaign.local_contact_id else False }

	return jsonify(
		status = True,
		message = "Listado de Contactos",
		contacts = data
	)

@operacion_bp.route('/operacion/json/send_revision', methods=['POST'])
def json_send_revision():
	ids = request.form.getlist("id[]")
	for id in ids:
		ic_id = InstitutionsCampaigns.query.filter(InstitutionsCampaigns.id == id).first()

		tmp_institutions = Institutions()
		tmp_institutions.id = ic_id.institution_id
		tmp_institutions.status_id = 2
		if request.form.get("from_coord"):
			tmp_institutions.unset_user()
			tmp_institutions.set_coordination(date = None, time = None)
		tmp_institutions.set_status(campaign_institution_id = id)
			
	return jsonify(
		status = True,
		message = "Success"
	)

@operacion_bp.route('/operacion/json/send_coordinacion', methods=['POST'])
def json_send_coordinacion():
	ids = request.form.getlist("id[]")
	
	for id in ids:
		ic_id = InstitutionsCampaigns.query.filter(InstitutionsCampaigns.id == id).first()

		tmp_institutions = Institutions()
		tmp_institutions.id = ic_id.institution_id
		tmp_institutions.status_id = 7
		tmp_institutions.set_status(campaign_institution_id = id)

	return jsonify(
		status = True,
		message = "Success"
	)

@operacion_bp.route('/operacion/json/assign_user', methods=['POST'])
def json_assign_user():
	ids = request.form.getlist("id[]")
	user_id = request.form.get("user_id")
	to_status = request.form.get("to_status")
	
	for id in ids:
		ic_id = InstitutionsCampaigns.query.filter(InstitutionsCampaigns.id == id).first()

		institutions = Institutions()
		institution = institutions.get_by_id(ic_id.institution_id)
		institution.user_id = user_id
		institution.save()

		institution.status_id = to_status
		institution.set_status(campaign_institution_id = id)

	return jsonify(
		status = True,
		message = "Success"
	)

@operacion_bp.route('/operacion/json/send_ejecucion', methods=['POST'])
def json_send_ejecucion():

	ids = request.form.getlist("id[]")
	count_success = 0
	count_failed = 0

	itt_success = []
	itt_failed = []

	if request.form.get("from_coord"):
		# desde fase coordinación
		# establecimiento debe estar coordinado y debe tener un contacto local asignado
		for id in ids:
			ic_id = InstitutionsCampaigns.query.filter(InstitutionsCampaigns.id == id).first()

			institution = Institutions.query.filter(Institutions.id == ic_id.institution_id).first()

			if ic_id.local_contact_id is None:
				count_failed = count_failed + 1
				itt_failed.append("<li>"+institution.name+"</li>")
			else:
				if institution.status_id == 8:
					# está coordinado
					institution.status_id = 9
					institution.set_status(campaign_institution_id = id)
					count_success = count_success + 1
					itt_success.append(institution.name)
				else:
					count_failed = count_failed + 1
					itt_failed.append("<li>"+institution.name+"</li>")
		
		return jsonify(
			status = True,
			message = "Success",
			count_failed = count_failed,
			count_success = count_success,
			itt_success = itt_success,
			itt_failed = itt_failed
		)
	return jsonify(
		status = False,
		message = "Error"
	)