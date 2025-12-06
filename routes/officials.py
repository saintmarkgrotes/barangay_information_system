from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from models import ElectedOfficial, db
from utils import admin_required, save_uploaded_file, delete_file
import os

officials_bp = Blueprint('officials', __name__)


@officials_bp.route('/elected_officials')
@login_required
def list_officials():
    """List all elected officials"""
    chairman = ElectedOfficial.query.filter_by(position='Chairman').first()
    kagawads = ElectedOfficial.query.filter_by(position='Kagawad').order_by(
        ElectedOfficial.order.is_(None), 
        ElectedOfficial.order
    ).all()
    return render_template('elected_officials.html', chairman=chairman, kagawads=kagawads)


@officials_bp.route('/elected_officials/add', methods=['POST'])
@admin_required
def add_official():
    """Add a new elected official"""
    name = (request.form.get('name') or '').strip()
    position = request.form.get('position')
    order_raw = request.form.get('order')
    file = request.files.get('photo')
    
    # Validate input
    if not name or position not in ('Chairman', 'Kagawad'):
        flash('Invalid name or position.', 'warning')
        return redirect(url_for('officials.list_officials'))
    
    # Handle Chairman position
    if position == 'Chairman':
        if ElectedOfficial.query.filter_by(position='Chairman').first():
            flash('Chairman already exists. Please remove existing chairman first.', 'warning')
            return redirect(url_for('officials.list_officials'))
        official = ElectedOfficial(name=name, position='Chairman')
    else:
        # Handle Kagawad position
        count = ElectedOfficial.query.filter_by(position='Kagawad').count()
        if count >= 7:
            flash('Maximum 7 Kagawad allowed.', 'warning')
            return redirect(url_for('officials.list_officials'))
        order = int(order_raw) if order_raw else (count + 1)
        official = ElectedOfficial(name=name, position='Kagawad', order=order)
    
    # Handle photo upload
    if file and file.filename:
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'elected_officials')
        filename = save_uploaded_file(file, upload_folder, current_app.config['ALLOWED_EXTENSIONS'])
        if filename:
            official.photo_filename = filename
    
    db.session.add(official)
    db.session.commit()
    flash(f'{position} added successfully.', 'success')
    return redirect(url_for('officials.list_officials'))


@officials_bp.route('/elected_officials/edit/<int:id>', methods=['POST'])
@admin_required
def edit_official(id):
    """Edit an elected official"""
    official = ElectedOfficial.query.get_or_404(id)
    
    name = (request.form.get('name') or '').strip()
    position = request.form.get('position')
    order_raw = request.form.get('order')
    file = request.files.get('photo')
    
    # Validate input
    if not name or position not in ('Chairman', 'Kagawad'):
        flash('Invalid name or position.', 'warning')
        return redirect(url_for('officials.list_officials'))
    
    # Handle position change
    if position == 'Chairman':
        existing = ElectedOfficial.query.filter(
            ElectedOfficial.position == 'Chairman', 
            ElectedOfficial.id != official.id
        ).first()
        if existing:
            flash('Another Chairman already exists.', 'warning')
            return redirect(url_for('officials.list_officials'))
        official.position = 'Chairman'
        official.order = None
    else:
        official.position = 'Kagawad'
        official.order = int(order_raw) if order_raw else None
    
    official.name = name
    
    # Handle photo upload
    if file and file.filename:
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'elected_officials')
        
        # Delete old photo if exists
        if official.photo_filename:
            old_path = os.path.join(upload_folder, official.photo_filename)
            delete_file(old_path)
        
        # Save new photo
        filename = save_uploaded_file(file, upload_folder, current_app.config['ALLOWED_EXTENSIONS'])
        if filename:
            official.photo_filename = filename
    
    db.session.commit()
    flash('Official updated successfully.', 'success')
    return redirect(url_for('officials.list_officials'))


@officials_bp.route('/elected_officials/delete/<int:id>', methods=['POST'])
@admin_required
def delete_official(id):
    """Delete an elected official"""
    official = ElectedOfficial.query.get_or_404(id)
    
    # Delete photo if exists
    if official.photo_filename:
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'elected_officials')
        photo_path = os.path.join(upload_folder, official.photo_filename)
        delete_file(photo_path)
    
    db.session.delete(official)
    db.session.commit()
    flash('Official removed successfully.', 'success')
    return redirect(url_for('officials.list_officials'))