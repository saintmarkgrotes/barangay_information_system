from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from models import Admin, db
from utils import admin_required
from flask_bcrypt import Bcrypt

settings_bp = Blueprint('settings', __name__)
bcrypt = Bcrypt()


@settings_bp.route('/system_settings', methods=['GET', 'POST'])
@admin_required
def system_settings():
    """System settings page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            return _handle_password_change()
        elif action == 'create_user':
            return _handle_create_user()
    
    all_users = Admin.query.all()
    return render_template('system_settings.html', all_users=all_users)


def _handle_password_change():
    """Handle password change request"""
    current_pwd = request.form.get('current_password')
    new_pwd = request.form.get('new_password')
    confirm_pwd = request.form.get('confirm_password')
    
    # Validate input
    if not (current_pwd and new_pwd and confirm_pwd):
        flash('Please fill all password fields.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    if not bcrypt.check_password_hash(current_user.password, current_pwd):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('settings.system_settings'))
    
    if new_pwd != confirm_pwd:
        flash('New passwords do not match.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    if len(new_pwd) < 6:
        flash('Password must be at least 6 characters long.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    # Update password
    current_user.password = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('settings.system_settings'))


def _handle_create_user():
    """Handle user creation request"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'user')
    
    # Validate input
    if not (username and password):
        flash('Username and password are required.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    if Admin.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('settings.system_settings'))
    
    if role not in ('user', 'admin'):
        role = 'user'
    
    # Create user
    user = Admin(
        username=username, 
        password=bcrypt.generate_password_hash(password).decode('utf-8'), 
        role=role
    )
    db.session.add(user)
    db.session.commit()
    flash(f'User "{username}" created successfully.', 'success')
    return redirect(url_for('settings.system_settings'))


@settings_bp.route('/system_settings/delete_user/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    """Delete a user account"""
    if id == current_user.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('settings.system_settings'))
    
    user = Admin.query.get_or_404(id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('settings.system_settings'))