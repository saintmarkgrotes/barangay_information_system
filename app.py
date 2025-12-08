from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from flask_wtf import CSRFProtect

csrf = CSRFProtect()
# Import models and configuration
from models import db, Admin, User
from config import config

# Import blueprints
from routes.auth import auth_bp, bcrypt as auth_bcrypt
from routes.main import main_bp
from routes.residents import residents_bp
from routes.officials import officials_bp
from routes.households import households_bp
from routes.settings import settings_bp, bcrypt as settings_bcrypt
from routes.certificates import certificates_bp


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    csrf = CSRFProtect(app)
    
    # Ensure upload directory exists
    upload_dir = os.path.join(app.static_folder, 'uploads', 'elected_officials')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    
    # Initialize bcrypt for blueprints
    auth_bcrypt.init_app(app)
    settings_bcrypt.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Try loading as Admin first
        user = Admin.query.get(int(user_id))
        if user:
            return user
        # Try loading as User (resident)
        user = User.query.get(int(user_id))
        return user
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(residents_bp)
    app.register_blueprint(officials_bp)
    app.register_blueprint(households_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(certificates_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(debug=True)