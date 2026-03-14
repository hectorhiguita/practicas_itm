"""
Módulo de autenticación.
Actualmente soporta login local (usuario/contraseña).
Preparado para agregar OAuth de Microsoft 365 / Azure AD en el futuro.
"""
import hmac
from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
import os

from src.config import get_config
from src.api.auth.manager import AppUser

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _verify_local(username: str, password: str) -> bool:
    """Verifica credenciales locales contra variables de entorno."""
    config = get_config()
    user_match = hmac.compare_digest(username.lower(), config.ADMIN_USER.lower())
    if not user_match:
        return False
    if not config.ADMIN_PASSWORD_HASH:
        # Sin hash configurado → acceso bloqueado en producción
        return False
    return check_password_hash(config.ADMIN_PASSWORD_HASH, password)


# ── Punto de extensión OAuth ──────────────────────────────────────────────────
# Para agregar Microsoft 365 / Azure AD, implementar aquí:
#
# from msal import ConfidentialClientApplication
#
# @auth_bp.route('/microsoft')
# def microsoft_login():
#     msal_app = ConfidentialClientApplication(
#         client_id=config.AZURE_CLIENT_ID,
#         authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",
#         client_credential=config.AZURE_CLIENT_SECRET,
#     )
#     auth_url = msal_app.get_authorization_request_url(
#         scopes=["User.Read"],
#         redirect_uri=url_for('auth.microsoft_callback', _external=True),
#     )
#     return redirect(auth_url)
#
# @auth_bp.route('/microsoft/callback')
# def microsoft_callback():
#     # Intercambiar código por token, obtener perfil del usuario, llamar login_user()
#     ...
# ─────────────────────────────────────────────────────────────────────────────


@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'login.html')
    with open(static_path, 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

    if _verify_local(username, password):
        login_user(AppUser(username), remember=data.get('remember', False))
        return jsonify({'ok': True}), 200

    return jsonify({'error': 'Credenciales incorrectas'}), 401


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/auth/login')
