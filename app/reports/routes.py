from . import reports_bp
from flask import render_template, request
from flask_login import login_required
from app.admin.models import Campaigns
from app import app, db
from .functions import get_report_states_institutions, get_report_states_institutions_xlsx

@reports_bp.route("/reportes/establecimientos", methods=["GET","POST"])
@login_required
def report_states_institutions():

   period = None
   list = []

   if request.form.get('period'):
      period = request.form.get('period')

      list = get_report_states_institutions(period)

   periods = db.session.query(Campaigns.period).group_by(Campaigns.period)

   return render_template(
      "report_institutions.html", 
      title = "Sistema de respaldos - Establecimientos", 
      reports_module = True,
      reports_institution_module = True,
      institutions = list,
      periods = periods,
      period_selected = period)

@reports_bp.route("/reportes/establecimientos/descargar", methods=["GET"])
@login_required
def report_states_institutions_download():
   period = None

   if request.form.get('period'):
      period = request.form.get('period')

   return get_report_states_institutions_xlsx(period)