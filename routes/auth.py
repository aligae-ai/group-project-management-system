from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

from models import db, User

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.verify_password(form.password.data):
            from flask_login import login_user
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
