from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Resident, Household, PendingResident, db
from utils import admin_required, validate_resident_data, parse_date
import datetime

residents_bp = Blueprint('residents', __name__)


@residents_bp.route('/residents')
@login_required
def list_residents():
    """List all residents with search functionality"""
    search = request.args.get('search', '').strip()
    query = Resident.query
    
    if search:
        query = query.filter(Resident.first_name.ilike(f'{search}%'))
    
    residents_list = query.order_by(Resident.first_name).all()
    households = Household.query.order_by(Household.household_no).all()
    
    # Serialize residents for JSON/JavaScript
    safe_residents = []
    for r in residents_list:
        safe_residents.append({
            'id': r.id,
            'last_name': r.last_name,
            'first_name': r.first_name,
            'middle_name': r.middle_name,
            'gender': r.gender,
            'age': r.age,
            'purok': r.purok,
            'voter_status': r.voter_status,
            'senior_citizen': r.senior_citizen,
            'date_of_birth': r.date_of_birth.strftime("%Y-%m-%d") if r.date_of_birth else "",
            'place_of_birth': r.place_of_birth,
            'civil_status': r.civil_status,
            'citizenship': r.citizenship,
            'occupation': r.occupation,
            'household_id': r.household_id
        })

    return render_template('residents.html', residents=safe_residents, households=households)


@residents_bp.route('/add_resident', methods=['POST'])
@login_required
def add_resident():
    """Add a new resident (admin directly, user submits for approval)"""
    # Extract form data
    form_data = {
        'last_name': request.form.get('last_name', '').strip(),
        'first_name': request.form.get('first_name', '').strip(),
        'middle_name': request.form.get('middle_name', '').strip(),
        'gender': request.form.get('gender'),
        'age': request.form.get('age', '').strip(),
        'purok': request.form.get('purok', '').strip(),
        'voter_status': request.form.get('voter_status'),
        'senior_citizen': request.form.get('senior_citizen'),
    }
    
    # Validate required fields
    is_valid, error_message = validate_resident_data(form_data)
    if not is_valid:
        flash(error_message, 'warning')
        return redirect(url_for('residents.list_residents'))
    
    # Optional fields
    date_of_birth_str = request.form.get('date_of_birth', '').strip()
    dob = parse_date(date_of_birth_str)
    if date_of_birth_str and not dob:
        flash('Invalid date format.', 'warning')
        return redirect(url_for('residents.list_residents'))
    
    place_of_birth = request.form.get('place_of_birth', '').strip() or None
    civil_status = request.form.get('civil_status', '').strip() or None
    citizenship = request.form.get('citizenship', '').strip() or None
    occupation = request.form.get('occupation', '').strip() or None
    household_select = request.form.get('household_select')
    
    # Handle household assignment
    household_id = None
    new_household_data = {}
    
    if household_select == 'new':
        new_household_data = {
            'new_household_no': request.form.get('new_household_no', '').strip(),
            'new_region': request.form.get('new_region', '').strip(),
            'new_province': request.form.get('new_province', '').strip(),
            'new_city_municipality': request.form.get('new_city_municipality', '').strip(),
            'new_barangay': request.form.get('new_barangay', '').strip(),
            'new_purok': request.form.get('new_purok', '').strip()
        }
        
        if not new_household_data['new_household_no']:
            flash('Household number is required when creating new household.', 'warning')
            return redirect(url_for('residents.list_residents'))
            
    elif household_select and household_select != 'none':
        try:
            household_id = int(household_select)
        except (TypeError, ValueError):
            household_id = None
    
    # Admin adds directly, users submit for approval
    if current_user.role == 'admin':
        return _add_resident_as_admin(form_data, dob, place_of_birth, civil_status, 
                                      citizenship, occupation, household_select, 
                                      household_id, new_household_data)
    else:
        return _submit_resident_for_approval(form_data, dob, place_of_birth, civil_status,
                                            citizenship, occupation, household_id, 
                                            new_household_data)


def _add_resident_as_admin(form_data, dob, place_of_birth, civil_status, 
                          citizenship, occupation, household_select, 
                          household_id, new_household_data):
    """Add resident directly (admin only)"""
    if household_select == 'new':
        # Check if household number already exists
        existing = Household.query.filter_by(household_no=new_household_data['new_household_no']).first()
        if existing:
            flash('Household number already exists.', 'warning')
            return redirect(url_for('residents.list_residents'))
        
        # Create new household
        new_household = Household(
            household_no=new_household_data['new_household_no'],
            region=new_household_data['new_region'] or None,
            province=new_household_data['new_province'] or None,
            city_municipality=new_household_data['new_city_municipality'] or None,
            barangay=new_household_data['new_barangay'] or None,
            purok=new_household_data['new_purok'] or None
        )
        db.session.add(new_household)
        db.session.flush()
        household_id = new_household.id
    
    # Create resident
    resident = Resident(
        last_name=form_data['last_name'],
        first_name=form_data['first_name'],
        middle_name=form_data['middle_name'],
        gender=form_data['gender'],
        age=int(form_data['age']),
        purok=form_data['purok'],
        voter_status=form_data['voter_status'],
        senior_citizen=form_data['senior_citizen'],
        date_of_birth=dob,
        place_of_birth=place_of_birth,
        civil_status=civil_status,
        citizenship=citizenship,
        occupation=occupation,
        household_id=household_id
    )
    db.session.add(resident)
    db.session.commit()
    
    flash('Resident added successfully.', 'success')
    return redirect(url_for('residents.list_residents'))


def _submit_resident_for_approval(form_data, dob, place_of_birth, civil_status,
                                  citizenship, occupation, household_id, 
                                  new_household_data):
    """Submit resident for admin approval (non-admin users)"""
    pending = PendingResident(
        last_name=form_data['last_name'],
        first_name=form_data['first_name'],
        middle_name=form_data['middle_name'],
        gender=form_data['gender'],
        age=int(form_data['age']),
        purok=form_data['purok'],
        voter_status=form_data['voter_status'],
        senior_citizen=form_data['senior_citizen'],
        date_of_birth=dob,
        place_of_birth=place_of_birth,
        civil_status=civil_status,
        citizenship=citizenship,
        occupation=occupation,
        household_id=household_id,
        submitted_by=current_user.id,
        status='pending',
        **new_household_data
    )
    db.session.add(pending)
    db.session.commit()
    
    flash('Resident submitted for approval. Admin will review shortly.', 'info')
    return redirect(url_for('residents.pending_residents'))


@residents_bp.route('/edit_resident/<int:id>', methods=['POST'])
@admin_required
def edit_resident(id):
    """Edit an existing resident (admin only)"""
    resident = Resident.query.get_or_404(id)
    
    # Update basic fields
    resident.last_name = request.form.get('last_name', '').strip()
    resident.first_name = request.form.get('first_name', '').strip()
    resident.middle_name = request.form.get('middle_name', '').strip()
    resident.gender = request.form.get('gender')
    
    try:
        resident.age = int(request.form.get('age', 0))
    except ValueError:
        flash('Invalid age.', 'warning')
        return redirect(url_for('residents.list_residents'))
    
    resident.purok = request.form.get('purok', '').strip()
    resident.voter_status = request.form.get('voter_status')
    resident.senior_citizen = request.form.get('senior_citizen')
    resident.place_of_birth = request.form.get('place_of_birth', '').strip() or None
    resident.civil_status = request.form.get('civil_status', '').strip() or None
    resident.citizenship = request.form.get('citizenship', '').strip() or None
    resident.occupation = request.form.get('occupation', '').strip() or None
    
    # Update date of birth
    dob_str = request.form.get('date_of_birth', '').strip()
    resident.date_of_birth = parse_date(dob_str) if dob_str else None
    
    # Handle household update
    household_select = request.form.get('household_select')
    
    if household_select == 'new':
        new_household_no = request.form.get('new_household_no', '').strip()
        if not new_household_no:
            flash('Household number is required.', 'warning')
            return redirect(url_for('residents.list_residents'))
        
        existing = Household.query.filter_by(household_no=new_household_no).first()
        if existing:
            flash('Household number already exists.', 'warning')
            return redirect(url_for('residents.list_residents'))
        
        new_household = Household(
            household_no=new_household_no,
            region=request.form.get('new_region', '').strip() or None,
            province=request.form.get('new_province', '').strip() or None,
            city_municipality=request.form.get('new_city_municipality', '').strip() or None,
            barangay=request.form.get('new_barangay', '').strip() or None,
            purok=request.form.get('new_purok', '').strip() or None
        )
        db.session.add(new_household)
        db.session.flush()
        resident.household_id = new_household.id
    elif household_select and household_select != 'none':
        try:
            resident.household_id = int(household_select)
        except (TypeError, ValueError):
            resident.household_id = None
    else:
        resident.household_id = None
    
    db.session.commit()
    flash('Resident updated successfully.', 'success')
    return redirect(url_for('residents.list_residents'))


@residents_bp.route('/delete_resident/<int:id>', methods=['POST'])
@admin_required
def delete_resident(id):
    """Delete a resident (admin only)"""
    resident = Resident.query.get_or_404(id)
    db.session.delete(resident)
    db.session.commit()
    flash('Resident deleted successfully.', 'success')
    return redirect(url_for('residents.list_residents'))


@residents_bp.route('/resident_info/<int:id>')
@login_required
def resident_info(id):
    """View detailed resident information"""
    resident = Resident.query.get_or_404(id)
    return render_template('resident_info.html', resident=resident)


@residents_bp.route('/pending_residents')
@login_required
def pending_residents():
    """View pending resident submissions"""
    if current_user.role == 'admin':
        pending = PendingResident.query.filter_by(status='pending').order_by(
            PendingResident.submitted_at.desc()).all()
    else:
        pending = PendingResident.query.filter_by(submitted_by=current_user.id).order_by(
            PendingResident.submitted_at.desc()).all()
    
    return render_template('pending_residents.html', pending_residents=pending)


@residents_bp.route('/review_resident/<int:id>/<action>', methods=['POST'])
@admin_required
def review_resident(id, action):
    """Review pending resident (approve/reject)"""
    pending = PendingResident.query.get_or_404(id)
    
    if action == 'approve':
        household_id = pending.household_id
        
        # Handle new household creation if needed
        if pending.new_household_no:
            existing = Household.query.filter_by(household_no=pending.new_household_no).first()
            if existing:
                household_id = existing.id
            else:
                new_household = Household(
                    household_no=pending.new_household_no,
                    region=pending.new_region or None,
                    province=pending.new_province or None,
                    city_municipality=pending.new_city_municipality or None,
                    barangay=pending.new_barangay or None,
                    purok=pending.new_purok or None
                )
                db.session.add(new_household)
                db.session.flush()
                household_id = new_household.id
        
        # Create resident from pending data
        resident = Resident(
            last_name=pending.last_name,
            first_name=pending.first_name,
            middle_name=pending.middle_name,
            gender=pending.gender,
            age=pending.age,
            purok=pending.purok,
            voter_status=pending.voter_status,
            senior_citizen=pending.senior_citizen,
            date_of_birth=pending.date_of_birth,
            place_of_birth=pending.place_of_birth,
            civil_status=pending.civil_status,
            citizenship=pending.citizenship,
            occupation=pending.occupation,
            household_id=household_id
        )
        db.session.add(resident)
        
        pending.status = 'approved'
        pending.reviewed_by = current_user.id
        pending.reviewed_at = datetime.datetime.utcnow()
        
        db.session.commit()
        flash('Resident approved and added to the system.', 'success')
        
    elif action == 'reject':
        pending.status = 'rejected'
        pending.reviewed_by = current_user.id
        pending.reviewed_at = datetime.datetime.utcnow()
        db.session.commit()
        flash('Resident submission rejected.', 'info')
    
    return redirect(url_for('residents.pending_residents'))