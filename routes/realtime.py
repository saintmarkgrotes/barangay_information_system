from flask import Blueprint, Response, stream_with_context
from flask_login import login_required, current_user
from models import CertificateRequest, db
import json
import time
from datetime import datetime, timedelta

realtime_bp = Blueprint('realtime', __name__)


@realtime_bp.route('/stream/certificate-updates')
@login_required
def certificate_updates():
    """
    Server-Sent Events stream for real-time certificate request updates.
    Only accessible to admin users.
    """
    if current_user.role != 'admin':
        return Response("Unauthorized", status=403)
    
    def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to updates'})}\n\n"
        
        # Track last known request ID to detect new requests
        last_check_time = datetime.utcnow()
        
        while True:
            try:
                # Check for new certificate requests since last check
                new_requests = CertificateRequest.query.filter(
                    CertificateRequest.requested_at > last_check_time
                ).order_by(CertificateRequest.requested_at.desc()).all()
                
                # Check for status changes in recent requests (last 24 hours)
                from datetime import timedelta
                recent_time = datetime.utcnow() - timedelta(hours=24)
                updated_requests = CertificateRequest.query.filter(
                    CertificateRequest.reviewed_at > last_check_time,
                    CertificateRequest.requested_at > recent_time
                ).all()
                
                # Send new requests
                for request in new_requests:
                    data = {
                        'type': 'new_request',
                        'id': request.id,
                        'reference_number': request.reference_number,
                        'requester_name': request.requester_name,
                        'certificate_type': request.certificate_type,
                        'status': request.status,
                        'requested_at': request.requested_at.strftime('%b %d, %Y %I:%M %p'),
                        'requested_by': request.requester.username
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Send status updates
                for request in updated_requests:
                    data = {
                        'type': 'status_update',
                        'id': request.id,
                        'reference_number': request.reference_number,
                        'status': request.status,
                        'certificate_number': request.certificate_number
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Send heartbeat to keep connection alive
                if not new_requests and not updated_requests:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                # Update last check time
                last_check_time = datetime.utcnow()
                
                # Wait before next check (5 seconds)
                time.sleep(5)
                
            except GeneratorExit:
                # Client disconnected
                break
            except Exception as e:
                # Log error and continue
                print(f"SSE Error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                time.sleep(5)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@realtime_bp.route('/stream/resident-updates')
@login_required
def resident_updates():
    """
    Server-Sent Events stream for real-time resident certificate updates.
    Accessible to resident users for their own requests.
    """
    if current_user.role != 'resident':
        return Response("Unauthorized", status=403)
    
    def generate():
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to updates'})}\n\n"
        
        last_check_time = datetime.utcnow()
        
        while True:
            try:
                # Check for updates to this resident's requests
                updated_requests = CertificateRequest.query.filter(
                    CertificateRequest.requested_by == current_user.id,
                    CertificateRequest.reviewed_at > last_check_time
                ).all()
                
                for request in updated_requests:
                    data = {
                        'type': 'status_update',
                        'id': request.id,
                        'reference_number': request.reference_number,
                        'status': request.status,
                        'certificate_number': request.certificate_number,
                        'certificate_type': request.certificate_type
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                if not updated_requests:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                last_check_time = datetime.utcnow()
                time.sleep(5)
                
            except GeneratorExit:
                break
            except Exception as e:
                print(f"SSE Error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                time.sleep(5)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )