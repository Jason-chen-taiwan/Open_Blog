from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from blog import db, limiter
from blog.models import User
from blog.forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    flash('Registration is disabled. Please contact administrator.', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5/minute", error_message="Too many login attempts. Please try again later.")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            current_app.logger.info(f"Successful login for user: {user.email} (Admin: {user.is_administrator})")
            flash('Logged in successfully!')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('post.home'))
        current_app.logger.warning(f"Failed login attempt for email: {form.email.data}")
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('post.home'))
