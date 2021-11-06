import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from flask_moment import Moment
from flask_login import LoginManager

from flask_mail import Mail

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'upload') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
#app.config['MAIL_DEBUG'] = True


app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_USERNAME'] = 'ariel.arzu@outlook.com'
app.config['MAIL_PASSWORD'] = 'theProblemIsChoice.1991'
app.config['MAIL_DEFAULT_SENDER'] = 'ariel.arzu@outlook.com'

app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

moment = Moment(app)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
# en caso de querer ver una vista protegida, será redirigido a login
login_manager.login_view = "config.login"

migrate = Migrate(app, db)

from .config import config_bp
app.register_blueprint(config_bp)

from . import admin
app.register_blueprint(admin.admin_bp)

from .operacion import operacion_bp
app.register_blueprint(operacion_bp)

from .dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

from .scheduled_tasks import tasks_bp
app.register_blueprint(tasks_bp)

from .reports import reports_bp
app.register_blueprint(reports_bp)