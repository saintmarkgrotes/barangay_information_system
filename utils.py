from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import os
from werkzeug.utils import secure_filename


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in.', 'warning')
            return redirect(url_for('auth.login'))
        if getattr(current_user, 'role', 'user') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder, allowed_extensions):
    """
    Save uploaded file and return filename
    
    Args:
        file: FileStorage object
        upload_folder: Directory to save file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        str: Saved filename or None
    """
    if file and file.filename and allowed_file(file.filename, allowed_extensions):
        import datetime
        filename = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S_') + secure_filename(file.filename)
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        return filename
    return None


def delete_file(filepath):
    """Safely delete a file"""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    return False


def validate_resident_data(form_data):
    """
    Validate resident form data
    
    Args:
        form_data: Dictionary of form data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['last_name', 'first_name', 'gender', 'age', 'purok', 'voter_status', 'senior_citizen']
    
    for field in required_fields:
        if not form_data.get(field, '').strip():
            return False, f'{field.replace("_", " ").title()} is required.'
    
    try:
        age = int(form_data.get('age', 0))
        if age < 0:
            return False, 'Age must be a positive number.'
    except ValueError:
        return False, 'Age must be a valid number.'
    
    return True, None


def parse_date(date_string):
    """
    Parse date string to date object
    
    Args:
        date_string: Date string in YYYY-MM-DD format
        
    Returns:
        date object or None
    """
    if not date_string:
        return None
    
    import datetime
    try:
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None