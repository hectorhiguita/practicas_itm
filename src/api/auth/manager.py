"""
Configuración de Flask-Login y clase de usuario de la aplicación.
Soporta: admin local (config) y asesores (BD).
"""
from flask_login import LoginManager, UserMixin
from src.config import get_config

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'


class AppUser(UserMixin):
    """
    Usuario en sesión.
    - role='admin'  → usuario administrador (credenciales en config/env)
    - role='asesor' → asesor de prácticas (credenciales en BD)
    """
    def __init__(self, user_id: str, username: str, role: str = 'admin', asesor_id: int = None):
        self.id = user_id          # 'admin' | 'asesor_<id>'
        self.username = username
        self.role = role
        self.asesor_id = asesor_id

    @property
    def is_admin(self):
        return self.role == 'admin'


@login_manager.user_loader
def load_user(user_id: str):
    if user_id == 'admin':
        config = get_config()
        return AppUser('admin', config.ADMIN_USER, role='admin')

    if user_id.startswith('asesor_'):
        try:
            asesor_db_id = int(user_id.split('_', 1)[1])
        except (ValueError, IndexError):
            return None
        from src.database.connection import get_session
        from src.models.base import Asesor
        db = get_session()
        try:
            asesor = db.query(Asesor).filter(
                Asesor.id == asesor_db_id,
                Asesor.activo == True,
            ).first()
            if asesor and asesor.username:
                return AppUser(user_id, asesor.username, role='asesor', asesor_id=asesor.id)
        finally:
            db.close()

    return None
