import smtplib
from email.message import EmailMessage
from src.config import EMAIL_CONFIG

def send_welcome_email(to_email):
    msg = EmailMessage()
    msg["Subject"] = "¡Bienvenido!"
    msg["From"] = EMAIL_CONFIG["USER"]
    msg["To"] = to_email

    msg.set_content("""
Hola 👋

Gracias por registrarte.
Pronto recibirás más información.

Equipo del sistema EcoEnergy
""")

    with smtplib.SMTP(EMAIL_CONFIG["HOST"], EMAIL_CONFIG["PORT"]) as server:
        server.starttls()
        server.login(
            EMAIL_CONFIG["USER"],
            EMAIL_CONFIG["PASSWORD"]
        )
        server.send_message(msg)
