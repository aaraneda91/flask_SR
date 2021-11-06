from flask import render_template, Blueprint, request, url_for, redirect
from . import config_bp
from flask_login import current_user, login_user, logout_user, login_required
from app import login_manager
from .forms import LoginForm
from app.admin.models import Users, Institutions
from app.logs.models import LogLogin

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

@config_bp.route("/")
@login_required
def index():
	return redirect(url_for('dashboard.dashboard'))

@config_bp.route("/usuarios")
def users():
	title = "Usuarios - Sistema de respaldos"
	return render_template("tables.html", title = title)

@config_bp.route("/detalle")
def detail():
	title = "Usuarios - Sistema de respaldos"
	return render_template("detalle.html", title = title)

@config_bp.route("/404")
def not_found():
	return render_template("404.html")

@config_bp.route("/login", methods=["POST","GET"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard.dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.get_by_username(form.username.data)
		if user is not None and user.check_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			next_page = request.args.get('config.next')
			log_login = LogLogin()
			log_login.user_id = user.id
			log_login.setLog()
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('dashboard.dashboard')
			return redirect(next_page)
	return render_template("login.html", form=form)

@config_bp.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('config.login'))