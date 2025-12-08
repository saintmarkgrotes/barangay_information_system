# routes/certificates.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, CertificateRequest, CertificateTemplate, BarangaySettings, Resident
from utils import admin_required
import datetime
import random
import string
import qrcode
from io import BytesIO
import base64

certificates_bp = Blueprint('certificates', __name__)


def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_reference_number():
    """Generate unique reference number"""
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CERT-{timestamp}-{random_str}"


def generate_certificate_number(cert_type):
    """Generate certificate number based on type"""
    year = datetime.datetime.utcnow().year
    count = CertificateRequest.query.filter_by(
        certificate_type=cert_type,
        status='approved'
    ).count() + 1
    
    type_code = {
        'Certificate of Indigency': 'CI',
        'Barangay Clearance': 'BC',
        'Certificate of Residency': 'CR',
        'Certificate of Good Moral': 'CGM',
        'Business Clearance': 'BUS'
    }.get(cert_type, 'CERT')
    
    return f"{type_code}-{year}-{count:04d}"


@certificates_bp.route('/resident-portal')
@login_required
def resident_portal():
    """Resident-only portal for certificate requests"""
    if current_user.role != 'resident':
        flash('Access denied. This portal is for residents only.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get resident's certificate requests
    requests = CertificateRequest.query.filter_by(
        requested_by=current_user.id
    ).order_by(CertificateRequest.requested_at.desc()).all()
    
    # Get statistics
    stats = {
        'total': len(requests),
        'pending': sum(1 for r in requests if r.status == 'pending'),
        'approved': sum(1 for r in requests if r.status == 'approved'),
        'rejected': sum(1 for r in requests if r.status == 'rejected')
    }
    
    return render_template('certificates/resident_portal.html', requests=requests, stats=stats)


@certificates_bp.route('/certificates')
@login_required
def list_certificates():
    """View certificate requests (user sees own, admin sees all)"""
    # Redirect residents to their portal
    if current_user.role == 'resident':
        return redirect(url_for('certificates.resident_portal'))
    
    if current_user.role == 'admin':
        requests = CertificateRequest.query.order_by(
            CertificateRequest.requested_at.desc()
        ).all()
    else:
        requests = CertificateRequest.query.filter_by(
            requested_by=current_user.id
        ).order_by(CertificateRequest.requested_at.desc()).all()
    
    # Get statistics
    stats = {
        'total': len(requests),
        'pending': sum(1 for r in requests if r.status == 'pending'),
        'approved': sum(1 for r in requests if r.status == 'approved'),
        'rejected': sum(1 for r in requests if r.status == 'rejected')
    }
    
    return render_template('certificates/list.html', requests=requests, stats=stats)


@certificates_bp.route('/certificates/request', methods=['GET', 'POST'])
@login_required
def request_certificate():
    """Request a new certificate"""
    if request.method == 'POST':
        # Get form data
        certificate_type = request.form.get('certificate_type')
        purpose = request.form.get('purpose', '').strip()
        requester_name = request.form.get('requester_name', '').strip()
        requester_address = request.form.get('requester_address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        resident_id = request.form.get('resident_id')
        
        # For resident role, auto-fill name and contact if not provided
        if current_user.role == 'resident':
            if not requester_name and current_user.full_name:
                requester_name = current_user.full_name
            if not contact_number and current_user.contact_number:
                contact_number = current_user.contact_number
        
        # Validate
        if not all([certificate_type, purpose, requester_name, requester_address]):
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('certificates.request_certificate'))
        
        # Create request
        cert_request = CertificateRequest(
            reference_number=generate_reference_number(),
            resident_id=int(resident_id) if resident_id and resident_id != 'none' else None,
            requester_name=requester_name,
            requester_address=requester_address,
            contact_number=contact_number or None,
            certificate_type=certificate_type,
            purpose=purpose,
            status='pending',
            requested_by=current_user.id
        )
        
        if current_user.role == 'resident':
            # Verify the resident_id belongs to current user if provided
            if resident_id and resident_id != 'none':
                resident = Resident.query.get(int(resident_id))
                if not resident:
                    flash('Invalid resident selection.', 'danger')
                    return redirect(url_for('certificates.request_certificate'))
        
        db.session.add(cert_request)
        db.session.commit()
        
        flash(f'Certificate request submitted successfully! Reference: {cert_request.reference_number}', 'success')
        
        # Redirect based on role
        if current_user.role == 'resident':
            return redirect(url_for('certificates.resident_portal'))
        return redirect(url_for('certificates.list_certificates'))
    
    # GET request - show form
    # Only load residents for admin/user roles
    residents = []
    if current_user.role != 'resident':
        residents = Resident.query.order_by(Resident.last_name, Resident.first_name).all()
    
    certificate_types = [
        'Certificate of Indigency',
        'Barangay Clearance',
        'Certificate of Residency',
        'Certificate of Good Moral',
        'Business Clearance',
        'Other'
    ]
    
    return render_template('certificates/request_form.html', 
                         residents=residents, 
                         certificate_types=certificate_types)


@certificates_bp.route('/certificates/<int:id>')
@login_required
def view_certificate(id):
    """View certificate details"""
    from sqlalchemy.orm import joinedload
    requests = CertificateRequest.query.options(
        joinedload(CertificateRequest.requester),
        joinedload(CertificateRequest.reviewer)
    ).order_by(...)
    
    # Security check - users can only view their own
    if current_user.role != 'admin' and cert.requested_by != current_user.id:
        flash('Access denied.', 'danger')
        if current_user.role == 'resident':
            return redirect(url_for('certificates.resident_portal'))
        return redirect(url_for('certificates.list_certificates'))
    
    return render_template('certificates/view.html', certificate=cert)


@certificates_bp.route('/certificates/<int:id>/approve', methods=['POST'])
@admin_required
def approve_certificate(id):
    """Approve certificate request"""
    cert = CertificateRequest.query.get_or_404(id)
    
    if cert.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('certificates.admin_certificates'))
    
    cert.status = 'approved'
    cert.reviewed_by = current_user.id
    cert.reviewed_at = datetime.datetime.utcnow()
    cert.certificate_number = generate_certificate_number(cert.certificate_type)
    cert.issued_date = datetime.date.today()
    
    db.session.commit()
    
    flash(f'Certificate approved! Number: {cert.certificate_number}', 'success')
    return redirect(url_for('certificates.admin_certificates'))


@certificates_bp.route('/certificates/<int:id>/reject', methods=['POST'])
@admin_required
def reject_certificate(id):
    """Reject certificate request"""
    cert = CertificateRequest.query.get_or_404(id)
    
    if cert.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('certificates.admin_certificates'))
    
    reason = request.form.get('rejection_reason', '').strip()
    
    cert.status = 'rejected'
    cert.reviewed_by = current_user.id
    cert.reviewed_at = datetime.datetime.utcnow()
    cert.rejection_reason = reason or 'No reason provided'
    
    db.session.commit()
    
    flash('Certificate request rejected.', 'info')
    return redirect(url_for('certificates.admin_certificates'))


@certificates_bp.route('/admin/certificates')
@admin_required
def admin_certificates():
    """Admin view of all certificate requests"""
    status_filter = request.args.get('status', 'all')
    
    query = CertificateRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(CertificateRequest.requested_at.desc()).all()
    
    # Statistics
    all_requests = CertificateRequest.query.all()
    stats = {
        'total': len(all_requests),
        'pending': sum(1 for r in all_requests if r.status == 'pending'),
        'approved': sum(1 for r in all_requests if r.status == 'approved'),
        'rejected': sum(1 for r in all_requests if r.status == 'rejected')
    }
    
    return render_template('certificates/admin_list.html', 
                         requests=requests, 
                         stats=stats, 
                         current_filter=status_filter)


@certificates_bp.route('/certificates/<int:id>/print')
@login_required
def print_certificate(id):
    """Generate printable certificate"""
    cert = CertificateRequest.query.get_or_404(id)
    
    # Security check
    if current_user.role not in ['admin', 'resident'] or (
        current_user.role == 'resident' and cert.requested_by != current_user.id
    ):
        flash('Access denied.', 'danger')
        if current_user.role == 'resident':
            return redirect(url_for('certificates.resident_portal'))
        return redirect(url_for('certificates.list_certificates'))
    
    if cert.status != 'approved':
        flash('Certificate must be approved before printing.', 'warning')
        return redirect(url_for('certificates.view_certificate', id=id))
    
    # Get barangay settings
    settings = BarangaySettings.query.first()
    if not settings:
        # Create default settings if none exist
        settings = BarangaySettings(
            barangay_name='Barangay Sample',
            municipality='Sample City',
            province='Sample Province',
            region='Region X',
            captain_name='Juan Dela Cruz'
        )
        db.session.add(settings)
        db.session.commit()
    
    return render_template('certificates/print.html', 
                         certificate=cert, 
                         settings=settings)


@certificates_bp.route('/certificates/<int:id>/download')
@login_required
def download_certificate(id):
    """Download certificate as PDF"""
    cert = CertificateRequest.query.get_or_404(id)
    
    # Security check
    if current_user.role not in ['admin', 'resident'] or (
        current_user.role == 'resident' and cert.requested_by != current_user.id
    ):
        flash('Access denied.', 'danger')
        if current_user.role == 'resident':
            return redirect(url_for('certificates.resident_portal'))
        return redirect(url_for('certificates.list_certificates'))
    
    if cert.status != 'approved':
        flash('Certificate must be approved before downloading.', 'warning')
        return redirect(url_for('certificates.view_certificate', id=id))
    
    # Generate PDF using WeasyPrint
    try:
        from weasyprint import HTML, CSS
        from flask import render_template_string
        import tempfile
        
        settings = BarangaySettings.query.first()
        html_content = render_template('certificates/print.html', 
                                      certificate=cert, 
                                      settings=settings)
        
        # Generate PDF
        pdf = HTML(string=html_content).write_pdf()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(pdf)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{cert.certificate_type.replace(' ', '_')}_{cert.certificate_number}.pdf",
            mimetype='application/pdf'
        )
    except ImportError:
        flash('PDF generation not available. Please use print function.', 'warning')
        return redirect(url_for('certificates.print_certificate', id=id))


@certificates_bp.route('/admin/barangay-settings', methods=['GET', 'POST'])
@admin_required
def barangay_settings():
    """Manage barangay settings for certificates"""
    settings = BarangaySettings.query.first()
    
    if request.method == 'POST':
        if not settings:
            settings = BarangaySettings()
            db.session.add(settings)
        
        settings.barangay_name = request.form.get('barangay_name', '').strip()
        settings.municipality = request.form.get('municipality', '').strip()
        settings.province = request.form.get('province', '').strip()
        settings.region = request.form.get('region', '').strip()
        settings.contact_number = request.form.get('contact_number', '').strip()
        settings.email_address = request.form.get('email_address', '').strip()
        settings.captain_name = request.form.get('captain_name', '').strip()
        settings.secretary_name = request.form.get('secretary_name', '').strip()
        settings.treasurer_name = request.form.get('treasurer_name', '').strip()
        
        db.session.commit()
        flash('Barangay settings updated successfully!', 'success')
        return redirect(url_for('certificates.barangay_settings'))
    
    return render_template('certificates/settings.html', settings=settings)