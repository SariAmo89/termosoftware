import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


# INITIALISIERENG
app = Flask(__name__)
bootstrap = Bootstrap(app)

# CONFIGURATION
# erforderlich für Sitzungscookies
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess' 

# DATENBANK CONFIGS
# Pfad festlegen
basedir = os.path.abspath(os.path.dirname(__file__))
# die Datenbank-Datei in der Instanz erstellen
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# keine Track modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Datenbank einstellen und die Instanz in 'db' speichern
db = SQLAlchemy(app)


# Setze den Thread auf None
global thread
thread = None

# Push Kontext
app.app_context().push()


# DB MIGRATION
Migrate(app,db)


# LOGIN CONFIGS
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"


# BLUEPRINT CONFIG
from ThermoSoftware.error_pages.handlers import error_pages
from ThermoSoftware.core.views import core
from ThermoSoftware.users.views import users

app.register_blueprint(error_pages)
app.register_blueprint(core)
app.register_blueprint(users)



