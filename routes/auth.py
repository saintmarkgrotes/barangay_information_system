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
        
        # FIXED: Verify that the person exists in the Resident database
        # Normalize the full name for comparison
        full_name_lower = full_name.lower().strip()
        
        # Split name into parts and clean them
        name_parts = [part.strip() for part in full_name_lower.split() if part.strip()]
        
        if len(name_parts) < 2:
            flash('Please enter your full name (at least first and last name).', 'warning')
            return render_template('register.html')
        
        # Search for matching resident
        resident = None
        
        # Get all residents and check each one
        all_residents = Resident.query.all()
        
        for r in all_residents:
            # Build variations of the resident's full name
            resident_names = []
            
            # Normalize resident data
            first = r.first_name.lower().strip() if r.first_name else ""
            middle = r.middle_name.lower().strip() if r.middle_name else ""
            last = r.last_name.lower().strip() if r.last_name else ""
            
            # Generate possible name combinations
            if first and last:
                resident_names.append(f"{first} {last}")  # First Last
            
            if first and middle and last:
                resident_names.append(f"{first} {middle} {last}")  # First Middle Last
                resident_names.append(f"{first} {middle[0]} {last}")  # First M. Last (initial)
                resident_names.append(f"{first} {middle[0]}. {last}")  # First M. Last (with period)
            
            if last and first:
                resident_names.append(f"{last} {first}")  # Last First (reversed)
            
            if last and first and middle:
                resident_names.append(f"{last} {first} {middle}")  # Last First Middle
            
            # Check if any combination matches the input
            input_name = " ".join(name_parts)
            
            for resident_name in resident_names:
                if input_name == resident_name:
                    resident = r
                    break
            
            if resident:
                break
        
        # If resident not found in database, deny registration
        if not resident:
            flash(
                'Your name was not found in our resident records. '
                'Please make sure you enter your name exactly as registered '
                '(e.g., "Juan Dela Cruz" or "Juan M Dela Cruz"), '
                'or contact the barangay office for assistance.',
                'danger'
            )
            return render_template('register.html')
        
        # Check if this resident already has an account
        # Check both by full_name match and by constructing the resident's full name
        resident_full_name_variations = [
            f"{resident.first_name} {resident.middle_name} {resident.last_name}".strip(),
            f"{resident.first_name} {resident.last_name}".strip(),
        ]
        
        existing_resident_account = Admin.query.filter(
            Admin.role == 'resident',
            db.or_(
                Admin.full_name == full_name,
                Admin.full_name.in_(resident_full_name_variations)
            )
        ).first()
        
        if existing_resident_account:
            flash(
                'An account for this resident already exists. '
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