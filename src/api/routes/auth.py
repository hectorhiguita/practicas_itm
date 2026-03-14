"""
Módulo de autenticación.
Soporta login local (admin por config, asesores por BD).
Preparado para agregar OAuth de Microsoft 365 / Azure AD en el futuro.
"""
import hmac
import os
from flask import Blueprint, request, jsonify, redirect
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from src.config import get_config
from src.api.auth.manager import AppUser

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _verify_local(username: str, password: str):
    """
    Verifica credenciales. Retorna AppUser si son válidas, None si no.
    Orden de verificación: 1) admin (config/env), 2) asesores (BD).
    """
    config = get_config()

    # 1) Admin
    if hmac.compare_digest(username.lower(), config.ADMIN_USER.lower()):
        if config.ADMIN_PASSWORD_HASH and check_password_hash(config.ADMIN_PASSWORD_HASH, password):
            return AppUser('admin', config.ADMIN_USER, role='admin')
        return None  # usuario es admin pero contraseña incorrecta → no seguir

    # 2) Asesor en BD
    from src.database.connection import get_session
    from src.models.base import Asesor
    db = get_session()
    try:
        asesor = db.query(Asesor).filter(
            Asesor.username == username.strip().lower(),
            Asesor.activo == True,
        ).first()
        if asesor and asesor.password_hash and check_password_hash(asesor.password_hash, password):
            return AppUser(f'asesor_{asesor.id}', asesor.username, role='asesor', asesor_id=asesor.id)
    finally:
        db.close()

    return None


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

    user = _verify_local(username, password)
    if user:
        login_user(user, remember=data.get('remember', False))
        return jsonify({'ok': True, 'role': user.role}), 200

    return jsonify({'error': 'Credenciales incorrectas'}), 401


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/auth/login')
