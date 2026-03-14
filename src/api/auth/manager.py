"""
Configuración de Flask-Login y clase de usuario de la aplicación.
"""
from flask_login import LoginManager, UserMixin
from src.config import get_config

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'


class AppUser(UserMixin):
    """Usuario en sesión. Actualmente solo soporta un admin local."""
    def __init__(self, username: str):
        self.id = username

    @property
    def username(self):
        return self.id


@login_manager.user_loader
def load_user(user_id: str):
    config = get_config()
    if user_id.lower() == config.ADMIN_USER.lower():
        return AppUser(user_id)
    return None
