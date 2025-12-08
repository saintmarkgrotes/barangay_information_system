# migrate_certificates.py
from app import create_app
from models import db
import sqlite3

app = create_app('development')

with app.app_context():
    # Drop and recreate the table (WARNING: This will delete existing certificate data)
    db.drop_all()
    db.create_all()
    print("✓ Database updated successfully!")