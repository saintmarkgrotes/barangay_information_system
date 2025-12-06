from app import create_app
from models import db, BarangaySettings

app = create_app('development')

with app.app_context():
    # Check if settings exist
    settings = BarangaySettings.query.first()
    
    if not settings:
        settings = BarangaySettings(
            barangay_name='Barangay San Jose',
            municipality='Calbayog City',
            province='Samar',
            region='Region VIII (Eastern Visayas)',
            captain_name='Juan Dela Cruz',
            secretary_name='Maria Santos'
        )
        db.session.add(settings)
        db.session.commit()
        print("✓ Default barangay settings created!")
    else:
        print("✓ Barangay settings already exist")