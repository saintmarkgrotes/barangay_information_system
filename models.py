from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()


class Admin(db.Model, UserMixin):
    """Admin, user, and resident accounts"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # admin, user, resident
    full_name = db.Column(db.String(200), nullable=True)  # For resident accounts
    contact_number = db.Column(db.String(20), nullable=True)  # For resident accounts


class User(db.Model, UserMixin):
    """Regular user accounts linked to residents"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    resident = db.relationship('Resident', backref='user_account', uselist=False)
    
    @property
    def role(self):
        return 'resident'


class Household(db.Model):
    """Household information"""
    id = db.Column(db.Integer, primary_key=True)
    household_no = db.Column(db.String(50), unique=True, nullable=False)
    region = db.Column(db.String(50), nullable=True)
    province = db.Column(db.String(100), nullable=True)
    city_municipality = db.Column(db.String(150), nullable=True)
    barangay = db.Column(db.String(150), nullable=True)
    purok = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    members = db.relationship('Resident', back_populates='household', lazy='dynamic')


class Resident(db.Model):
    """Resident information"""
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    middle_name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    purok = db.Column(db.String(100), nullable=False)
    voter_status = db.Column(db.String(20), nullable=False, default='Voter')
    senior_citizen = db.Column(db.String(5), nullable=False, default='No')
    date_of_birth = db.Column(db.Date, nullable=True)
    place_of_birth = db.Column(db.String(150), nullable=True)
    civil_status = db.Column(db.String(50), nullable=True)
    citizenship = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(150), nullable=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=True)
    household = db.relationship('Household', back_populates='members')


class PendingResident(db.Model):
    """Pending resident approvals"""
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    middle_name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    purok = db.Column(db.String(100), nullable=False)
    voter_status = db.Column(db.String(20), nullable=False, default='Voter')
    senior_citizen = db.Column(db.String(5), nullable=False, default='No')
    date_of_birth = db.Column(db.Date, nullable=True)
    place_of_birth = db.Column(db.String(150), nullable=True)
    civil_status = db.Column(db.String(50), nullable=True)
    citizenship = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(150), nullable=True)
    household_id = db.Column(db.Integer, nullable=True)
    new_household_no = db.Column(db.String(50), nullable=True)
    new_region = db.Column(db.String(50), nullable=True)
    new_province = db.Column(db.String(100), nullable=True)
    new_city_municipality = db.Column(db.String(150), nullable=True)
    new_barangay = db.Column(db.String(150), nullable=True)
    new_purok = db.Column(db.String(50), nullable=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    submitter = db.relationship('Admin', foreign_keys=[submitted_by], backref='pending_submissions')
    reviewer = db.relationship('Admin', foreign_keys=[reviewed_by], backref='reviewed_submissions')


class ElectedOfficial(db.Model):
    """Elected officials (Chairman and Kagawads)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class BarangayEvent(db.Model):
    """Barangay events"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin = db.relationship('Admin', backref='events')

class CertificateRequest(db.Model):
    """Certificate requests from residents"""
    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Requester information
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=True)
    requester_name = db.Column(db.String(300), nullable=False)
    requester_address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    
    # Certificate details
    certificate_type = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    
    # Request tracking
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, ready
    requested_by_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    requested_by_admin = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Admin action tracking
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Certificate details when approved
    certificate_number = db.Column(db.String(50), nullable=True)
    issued_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    resident = db.relationship('Resident', backref='certificate_requests', foreign_keys=[resident_id])
    user_requester = db.relationship('User', foreign_keys=[requested_by_user], backref='user_certificate_requests')
    admin_requester = db.relationship('Admin', foreign_keys=[requested_by_admin], backref='admin_certificate_requests')
    reviewer = db.relationship('Admin', foreign_keys=[reviewed_by], backref='certificate_requests_reviewed')


class CertificateTemplate(db.Model):
    """Templates for different certificate types"""
    id = db.Column(db.Integer, primary_key=True)
    certificate_type = db.Column(db.String(100), unique=True, nullable=False)
    template_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Template content
    header_text = db.Column(db.Text, nullable=True)
    body_template = db.Column(db.Text, nullable=False)
    footer_text = db.Column(db.Text, nullable=True)
    
    # Barangay information
    barangay_name = db.Column(db.String(200), nullable=True)
    barangay_address = db.Column(db.Text, nullable=True)
    
    # Officials
    captain_name = db.Column(db.String(200), nullable=True)
    secretary_name = db.Column(db.String(200), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class BarangaySettings(db.Model):
    """Global barangay settings for certificates"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Barangay Information
    barangay_name = db.Column(db.String(200), nullable=False)
    municipality = db.Column(db.String(200), nullable=False)
    province = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    
    # Contact Information
    contact_number = db.Column(db.String(50), nullable=True)
    email_address = db.Column(db.String(100), nullable=True)
    
    # Current Officials
    captain_name = db.Column(db.String(200), nullable=False)
    secretary_name = db.Column(db.String(200), nullable=True)
    treasurer_name = db.Column(db.String(200), nullable=True)
    
    # Logo and seal
    logo_filename = db.Column(db.String(255), nullable=True)
    seal_filename = db.Column(db.String(255), nullable=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)