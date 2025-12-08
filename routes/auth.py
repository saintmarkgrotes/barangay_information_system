from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import Admin, Resident, db
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role == 'resident':
            return redirect(url_for('certificates.resident_portal'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password.', 'warning')
            return render_template('login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and bcrypt.check_password_hash(admin.password, password):
            login_user(admin)
            flash('Logged in successfully.', 'success')
            
            # Redirect based on role
            if admin.role == 'resident':
                return redirect(url_for('certificates.resident_portal'))
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle resident registration - Only for registered residents"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        
        # Basic validation
        if not all([username, password, confirm_password, full_name]):
            flash('Please fill in all required fields.', 'warning')
            return render_template('register.html')
        
        if len(username) < 4:
            flash('Username must be at least 4 characters long.', 'warning')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('register.html')
        
        # Check if username already exists
        existing_user = Admin.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
        
        # CRITICAL: Verify that the person exists in the Resident database
        # Parse the full name to search for resident
        name_parts = full_name.strip().split()
        
        if len(name_parts) < 2:
            flash('Please enter your full name (at least first and last name).', 'warning')
            return render_template('register.html')
        
        # Try to find matching resident
        # Common patterns: "FirstName LastName" or "FirstName MiddleName LastName"
        resident = None
        
        if len(name_parts) == 2:
            # Try: FirstName LastName
            first_name = name_parts[0]
            last_name = name_parts[1]
            resident = Resident.query.filter(
                Resident.first_name.ilike(first_name),
                Resident.last_name.ilike(last_name)
            ).first()
        elif len(name_parts) >= 3:
            # Try: FirstName MiddleName LastName
            first_name = name_parts[0]
            middle_name = name_parts[1]
            last_name = ' '.join(name_parts[2:])  # Handle multi-part last names
            
            resident = Resident.query.filter(
                Resident.first_name.ilike(first_name),
                Resident.middle_name.ilike(middle_name),
                Resident.last_name.ilike(last_name)
            ).first()
            
            # If not found, try without middle name
            if not resident:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
                resident = Resident.query.filter(
                    Resident.first_name.ilike(first_name),
                    Resident.last_name.ilike(last_name)
                ).first()
        
        # If resident not found in database, deny registration
        if not resident:
            flash(
                'Your name was not found in our resident records. '
                'Please make sure you are registered as a barangay resident first, '
                'or contact the barangay office for assistance.',
                'danger'
            )
            return render_template('register.html')
        
        # Check if this resident already has an account
        existing_resident_account = Admin.query.filter_by(
            role='resident',
            full_name=full_name
        ).first()
        
        if existing_resident_account:
            flash(
                'An account with this name already exists. '
                'If you forgot your password, please contact the barangay office.',
                'danger'
            )
            return render_template('register.html')
        
        # Create new resident user account
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Admin(
            username=username,
            password=hashed_password,
            role='resident',
            full_name=full_name,
            contact_number=contact_number
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(
            f'Registration successful, {resident.first_name}! You can now log in and request certificates.',
            'success'
        )
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))