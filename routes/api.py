from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import CertificateRequest, db
from datetime import datetime
from utils import admin_required

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/certificate-updates')
@login_required
@admin_required
def certificate_updates():
    """
    Fast polling endpoint for admin certificate updates.
    Returns only new/updated certificates since last check.
    """
    # Get timestamp from query parameter
    since_str = request.args.get('since', '')
    
    try:
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            # Default to 1 minute ago
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(minutes=1)
    except (ValueError, AttributeError):
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(minutes=1)
    
    updates = []
    
    # Check for new requests
    new_requests = CertificateRequest.query.filter(
        CertificateRequest.requested_at > since
    ).order_by(CertificateRequest.requested_at.desc()).all()
    
    for cert in new_requests:
        updates.append({
            'type': 'new_request',
            'id': cert.id,
            'reference_number': cert.reference_number,
            'requester_name': cert.requester_name,
            'certificate_type': cert.certificate_type,
            'status': cert.status,
            'requested_at': cert.requested_at.strftime('%b %d, %Y %I:%M %p'),
            'requested_by': cert.requester.username if cert.requester else 'Unknown'
        })
    
    # Check for status updates (approved/rejected)
    updated_requests = CertificateRequest.query.filter(
        CertificateRequest.reviewed_at > since,
        CertificateRequest.reviewed_at.isnot(None)
    ).all()
    
    for cert in updated_requests:
        updates.append({
            'type': 'status_update',
            'id': cert.id,
            'reference_number': cert.reference_number,
            'status': cert.status,
            'certificate_number': cert.certificate_number,
            'certificate_type': cert.certificate_type
        })
    
    return jsonify({
        'success': True,
        'updates': updates,
        'count': len(updates),
        'current_time': datetime.utcnow().isoformat() + 'Z'
    })


@api_bp.route('/api/resident-updates')
@login_required
def resident_updates():
    """
    Fast polling endpoint for resident certificate status updates.
    Returns only updates for the current resident's requests.
    """
    if current_user.role != 'resident':
        return jsonify({'error': 'Unauthorized'}), 403
    
    since_str = request.args.get('since', '')
    
    try:
        if since_str:
            since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
        else:
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(minutes=1)
    except (ValueError, AttributeError):
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(minutes=1)
    
    updates = []
    
    # Check for updates to this resident's requests
    updated_requests = CertificateRequest.query.filter(
        CertificateRequest.requested_by == current_user.id,
        CertificateRequest.reviewed_at > since,
        CertificateRequest.reviewed_at.isnot(None)
    ).all()
    
    for cert in updated_requests:
        updates.append({
            'type': 'status_update',
            'id': cert.id,
            'reference_number': cert.reference_number,
            'status': cert.status,
            'certificate_number': cert.certificate_number,
            'certificate_type': cert.certificate_type
        })
    
    return jsonify({
        'success': True,
        'updates': updates,
        'count': len(updates),
        'current_time': datetime.utcnow().isoformat() + 'Z'
    })


@api_bp.route('/api/certificate-stats')
@login_required
@admin_required
def certificate_stats():
    """
    Quick endpoint to get current statistics.
    Useful for dashboard updates.
    """
    all_requests = CertificateRequest.query.all()
    
    stats = {
        'total': len(all_requests),
        'pending': sum(1 for r in all_requests if r.status == 'pending'),
        'approved': sum(1 for r in all_requests if r.status == 'approved'),
        'rejected': sum(1 for r in all_requests if r.status == 'rejected')
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })


@api_bp.route('/api/health')
def health_check():
    """
    Simple health check endpoint.
    Returns server status and timestamp.
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'barangay-certificate-system'
    })