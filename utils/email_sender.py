import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configs.email_config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL


async def send_otp_email(to_email: str, otp: str) -> None:
    message = MIMEMultipart()
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = "Password Reset OTP"

    body = f"""
    Your OTP for password reset is: {otp}

    This OTP is valid for 5 minutes. Do not share it with anyone.
    """
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, to_email, message.as_string())
