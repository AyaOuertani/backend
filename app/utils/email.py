from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List

from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, verification_code: str) :
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h1>Verification Code</h1>
            <p>Thank you for registering. Please use the following code to verify your account:</p>
            <h2>{verification_code}</h2>
            <p>This code will expire in {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutes.</p>
        </body>
        </html>
        """,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return{"message": "Verification email sent successfully."}