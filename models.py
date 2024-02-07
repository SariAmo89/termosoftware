from flask import Flask
from ThermoSoftware import db,login_manager,app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_security import UserMixin, RoleMixin, Security, SQLAlchemySessionUserDatastore
from flask_login import UserMixin
from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer


# LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Erstellen einer Tabelle in der Datenbank für die Zuweisung von Rollen
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))   

# Erstellen einer Tabelle in der Datenbank zur Speicherung von Rollen
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

# USER
class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer,primary_key=True)
    profile_image = db.Column(db.String(64),nullable=False,default='default_profile.png')
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users, backref='dynamic')

    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f"Username {self.username} -- Date: {self.date}"
    
    def has_role(self, role):                 # Hat user ... Role? -> True False
        return role in self.roles
    
    def which_role(self):                     # Welche Role hat er? -> Admin User
        for role in self.roles:
            if role == 'Admin':
                return 'Admin'
            else:
                return 'User'

    def get_id(self):
        return self.id

    def all_users(self):
        all_users=[(user.username) for user in User.query.order_by('username')]
        return all_users

# VOR DEN ERSTEN AUFRUF
@app.before_first_request
def create_tables():
    db.create_all()

# load users, roles for a session
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)
security._state.unauthorized_handler('/')