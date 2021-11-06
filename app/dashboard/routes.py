from flask import render_template, Blueprint, request, url_for, redirect, jsonify
from . import dashboard_bp
from flask_login import current_user, login_user, logout_user, login_required
from .models import Dashboard
from app.admin.models import Users, Institutions, Clients

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

	institutions = Institutions()
	intt_gestion = institutions.get_gestion()
	intt_revision = institutions.get_revision()
	intt_coordinacion = institutions.get_coordinacion()
	intt_ejecucion = institutions.get_ejecucion()
	intt_terminados = institutions.get_terminados()

	d = Dashboard()
	data = d.finished_per_clients()

	data_finished_per_month = d.finished_per_month()

	return render_template(
		"dashboard.html",
		intt_gestion = len(intt_gestion),
		intt_revision = len(intt_revision),
		intt_coordinacion = len(intt_coordinacion),
		intt_ejecucion = len(intt_ejecucion),
		intt_terminados = len(intt_terminados), 
		title = "Dashboard - Sistema de respaldos",
		finished_per_clients = data,
		data_finished_per_month = data_finished_per_month)

@dashboard_bp.route("/json/terminados_por_mes")
@login_required
def finished_per_month():

	d = Dashboard()
	data = d.finished_per_month()

	return jsonify(
		status = True,
		message = "Terminados por mes",
		data = data)

@dashboard_bp.route("/json/terminados_por_mes_y_clientes")
@login_required
def finished_per_month_and_clients():

	client = {}

	d = Dashboard()
	c = Clients.query.all()
	i = 0

	for c_data in c:
		if d.finished_per_month(client = str(c_data.id)):
			client[i] = {'client': c_data.name}
			client[i]['data'] = d.finished_per_month(client = str(c_data.id))
			i = i + 1

	return jsonify(
		status = True,
		message = "Terminados por mes y clientes",
		data=client)