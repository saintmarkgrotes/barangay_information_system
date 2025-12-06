from flask import Blueprint, render_template
from flask_login import login_required
from models import Household, Resident

households_bp = Blueprint('households', __name__)


@households_bp.route('/household_list')
@login_required
def list_households():
    """List all households"""
    households = Household.query.order_by(Household.household_no).all()
    return render_template('household_list.html', households=households)


@households_bp.route('/household/<int:id>')
@login_required
def household_detail(id):
    """View household details with members"""
    household = Household.query.get_or_404(id)
    members = household.members.order_by(Resident.last_name, Resident.first_name).all()
    return render_template('household_detail.html', household=household, members=members)