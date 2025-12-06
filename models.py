from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()


class Admin(db.Model, UserMixin):
    """Admin and user accounts"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')


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