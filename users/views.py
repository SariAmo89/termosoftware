from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from ThermoSoftware import db
from ThermoSoftware.models import User, Role
from ThermoSoftware.users.forms import deleteRoleForm,LoginForm,UpdateUserForm,RegistrationForm,deleteUserForm 
from ThermoSoftware.users.picture_handler import add_profile_pic
from sqlalchemy.exc import IntegrityError
from flask_security import roles_required

# Blueprint definieren
users = Blueprint('users',__name__)

# Registration
@users.route('/user_register', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def register():
    form = RegistrationForm()
    try:
        if form.validate_on_submit():
            user = User(email=form.email.data, username=form.username.data, password=form.password.data)
            role = Role.query.filter_by(id=form.role.data).first()
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            flash('User erfolgreich registriert!', 'success')
            return redirect(url_for('users.listusers'))
    except IntegrityError:
            flash('Name oder Passwort schon vergeben!', 'danger')
            return redirect(url_for('users.register'))

    return render_template('register.html',form=form, legend="Benutzer registrieren")

# login
@users.route('/user_login',methods=['GET','POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.check_password(form.password.data):

            login_user(user, form.remember_me.data)
            flash('Anmeldung erfolgreich!', 'success')

            next = request.args.get('next')

            if next ==None or not next[0]=='/':
                if User.has_role(current_user, 'Admin'):
                    next = url_for('users.listusers')
                else:
                    next = url_for('users.account') 

            return redirect(next)
        flash('Ungültiges Username oder Passwort!', "danger")

    return render_template('login.html',form=form,legend="Log in")


# logout
@users.route("/logout")
def logout():
    logout_user()
    flash('Logout erfolgreich!', 'success')
    return redirect(url_for("core.index"))


# Edit account (update UserForm)
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUserForm()
    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form, legend="Benutzer Information")

# Users view
@users.route('/listusers')
@login_required
@roles_required('Admin')
def listusers():
    headings = ("Id", "Name", "Date", "Role", "Email", "Picture")
    userTable = [[user.id, user.username, user.date, user.which_role(), user.email, user.profile_image] for user in User.query.all()]
    return render_template('listusers.html', headings=headings, table = userTable, legend="Benutzer Liste")

# Roles view
@users.route('/listroles')
@login_required
@roles_required('Admin')
def listroles():
    headings = ("Id", "Name")
    roleTable = [[role.id, role.name] for role in Role.query.all()]
    return render_template('listroles.html', headings=headings, table = roleTable, legend="Rollen Liste")


#################################################################
# HILFS-ROUTEN

# Delete User
@users.route('/users_delete', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def user_delete():
    form = deleteUserForm()
    form.target_username.choices=[(user.username) for user in User.query.order_by('username')]
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.target_username.data).first()
        if user.username == 'Admin':
            flash('Benützer Admin kann nicht gelöscht werden', 'danger')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('User gelöscht', 'danger')
        return redirect(url_for('users.listusers'))
    return render_template('delete.html', form=form, legend="User Löschen")

# Delete Role
@users.route('/role_delete', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def role_delete():
    form = deleteRoleForm()
    form.target_rolename.choices=[(role.name) for role in Role.query.order_by('id')]
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.target_rolename.data).first()
        if role.name == 'Admin':
            flash('Benützer Admin kann nicht gelöscht werden', 'danger')
        else:
            db.session.delete(role)
            db.session.commit()
            flash('Role gelöscht', 'danger')
        return redirect(url_for('role.listroles'))
    return render_template('delete_role.html', form=form, legend="Role Löschen")
