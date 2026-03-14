"""
Servicio de envío de correos electrónicos vía SMTP (O365 / smtp.office365.com).
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import get_config

logger = logging.getLogger(__name__)


def _build_credentials_html(nombre: str, username: str, password: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;color:#2C2C2C;max-width:560px;margin:0 auto;padding:24px;">
  <div style="background:linear-gradient(135deg,#1B1464,#56ACDE);padding:28px 32px;border-radius:10px 10px 0 0;text-align:center;">
    <h1 style="color:#fff;margin:0;font-size:20px;">Sistema de Prácticas Profesionales — ITM</h1>
    <p style="color:rgba(255,255,255,0.85);margin:8px 0 0;font-size:13px;">Acceso al sistema de gestión</p>
  </div>
  <div style="background:#f9f9f9;border:1px solid #E0E0E0;border-top:none;border-radius:0 0 10px 10px;padding:28px 32px;">
    <p>Hola <strong>{nombre}</strong>,</p>
    <p>Se ha creado tu cuenta de acceso al sistema de gestión de prácticas del ITM. Tus credenciales son:</p>
    <table style="width:100%;border-collapse:collapse;margin:16px 0;">
      <tr>
        <td style="padding:10px 14px;background:#fff;border:1px solid #E0E0E0;border-radius:6px 6px 0 0;font-weight:600;width:120px;">Usuario</td>
        <td style="padding:10px 14px;background:#fff;border:1px solid #E0E0E0;border-top:none;font-family:monospace;font-size:15px;">{username}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;background:#fff;border:1px solid #E0E0E0;border-top:none;border-radius:0 0 6px 6px;font-weight:600;">Contraseña</td>
        <td style="padding:10px 14px;background:#fff;border:1px solid #E0E0E0;border-top:none;font-family:monospace;font-size:15px;">{password}</td>
      </tr>
    </table>
    <p style="background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;font-size:13px;">
      <strong>⚠ Importante:</strong> Por seguridad, te recomendamos cambiar tu contraseña después de iniciar sesión por primera vez.
    </p>
    <p style="font-size:13px;color:#666;margin-top:24px;">
      Este correo fue generado automáticamente. Si tienes dudas, comunícate con el administrador del sistema.
    </p>
  </div>
</body>
</html>
"""


def send_credentials_email(to_email: str, nombre: str, username: str, password: str) -> bool:
    """
    Envía las credenciales de acceso al asesor recién creado.
    Retorna True si el envío fue exitoso, False si falló.
    """
    config = get_config()

    if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
        logger.warning("Email no configurado (MAIL_USERNAME/MAIL_PASSWORD vacíos). Credenciales no enviadas.")
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Tus credenciales de acceso — Prácticas ITM'
    msg['From']    = config.MAIL_FROM or config.MAIL_USERNAME
    msg['To']      = to_email

    html_body = _build_credentials_html(nombre, username, password)
    plain_body = (
        f"Hola {nombre},\n\n"
        f"Se ha creado tu cuenta en el sistema de prácticas ITM.\n\n"
        f"Usuario: {username}\n"
        f"Contraseña: {password}\n\n"
        f"Te recomendamos cambiar tu contraseña al iniciar sesión por primera vez."
    )

    msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT, timeout=15) as smtp:
            if config.MAIL_USE_TLS:
                smtp.starttls()
            smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            smtp.sendmail(msg['From'], [to_email], msg.as_string())
        logger.info(f"Credenciales enviadas a {to_email}")
        return True
    except Exception as exc:
        logger.error(f"Error al enviar credenciales a {to_email}: {exc}")
        return False
