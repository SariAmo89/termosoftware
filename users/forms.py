from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired
from flask_wtf.file import FileField,FileAllowed
from ThermoSoftware.models import User, Role

# LOGIN
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Passwort',validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Log In')

    def validate_password(form, field):
        if form.submit.data and not form.password.data:
            raise ValidationError('Bitte geben Sie Ihr Passwort an.')


# REGISTRATION
class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    username = StringField('Benutzername',validators=[DataRequired()])
    password = PasswordField('Passwort',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwörter müssen übereinstimmen!')])
    pass_confirm = PasswordField('Passwort bestätigen',validators=[DataRequired()])
    role = RadioField('Role wählen', choices=[(role.id, role.name) for role in Role.query.order_by('name')],validators=[InputRequired()])
    submit = SubmitField('Registrieren')

    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Die E-Mail wurde bereits registriert!')

    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Die E-Mail wurde bereits registriert!')
        

# UPDATE ACCOUNT
class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    username = StringField('Benutzername', validators=[DataRequired()])
    picture = FileField('Profilbild ändern', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Konto aktualisieren')

    def check_email(self, field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Die E-Mail wurde bereits registriert!')

    def check_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Benutzername ist schon vergeben!')


########## HILFS-FORMS ########

# DELETE USER
class deleteUserForm(FlaskForm):
    target_username = SelectField('User auswählen', coerce=str, validators=[InputRequired()])  # choices def in user_delete view
    submit = SubmitField('Löschen')

# DELETE ROLE
class deleteRoleForm(FlaskForm):
    target_rolename = SelectField('Role löschen', coerce=str, validators=[InputRequired()])
    submit = SubmitField('Löschen')
