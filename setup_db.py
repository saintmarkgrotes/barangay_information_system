from app import create_app
from models import db, Admin
from flask_bcrypt import Bcrypt


def setup_database(drop_first=False):
    """Initialize database and create default admin user"""
    app = create_app('development')
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        if drop_first:
            print('Dropping existing database tables (this will erase all data)...')
            db.drop_all()
        
        print('Creating database tables...')
        db.create_all()
        
        # Check if admin user exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Admin(username='admin', password=hashed_password, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  IMPORTANT: Change this password after first login!")
        else:
            # Reset admin password
            new_password = "admin123"
            admin.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            admin.role = 'admin'
            db.session.commit()
            print(f"✓ Password reset for user '{admin.username}'")
            print("  New password: admin123")
        
        print("\n✓ Database setup completed successfully!")


if __name__ == '__main__':
    import sys
    
    # Check if user wants to drop tables
    drop_tables = False
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        response = input('WARNING: This will delete all existing data. Continue? (yes/no): ')
        if response.lower() == 'yes':
            drop_tables = True
        else:
            print('Aborted.')
            sys.exit(0)
    
    setup_database(drop_first=drop_tables)