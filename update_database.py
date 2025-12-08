"""
Database update script to add full_name and contact_number columns to Admin table
Run this after updating your models.py
"""
from app import create_app
from models import db

app = create_app('development')

with app.app_context():
    # This will create any new tables and add new columns
    db.create_all()
    print("✓ Database updated successfully!")
    print("✓ Added full_name and contact_number columns to Admin table")
    print("\nYou can now:")
    print("1. Register new resident accounts via /register")
    print("2. Residents can access their portal at /resident-portal")