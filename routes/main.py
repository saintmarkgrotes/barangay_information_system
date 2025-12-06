from flask import Blueprint, render_template
from flask_login import login_required
from models import Resident

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with statistics"""
    total_population = Resident.query.count()
    total_males = Resident.query.filter_by(gender='Male').count()
    total_females = Resident.query.filter_by(gender='Female').count()
    total_voters = Resident.query.filter_by(voter_status='Voter').count()
    total_non_voters = Resident.query.filter_by(voter_status='Non-Voter').count()
    total_senior_citizens = Resident.query.filter_by(senior_citizen='Yes').count()

    return render_template('dashboard.html',
                           total_population=total_population,
                           total_males=total_males,
                           total_females=total_females,
                           total_voters=total_voters,
                           total_non_voters=total_non_voters,
                           total_senior_citizens=total_senior_citizens)