# This file makes the routes directory a Python package
# Import blueprints here if you want to use them from routes package directly

from .auth import auth_bp
from .main import main_bp
from .residents import residents_bp
from .officials import officials_bp
from .households import households_bp
from .settings import settings_bp
from .certificates import certificates_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'residents_bp',
    'officials_bp',
    'households_bp',
    'settings_bp',
    'certificates_bp'
]