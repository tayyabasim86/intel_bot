import os, smtplib, ssl
from email.message import EmailMessage

def send_email(subject: str, body: str):
    user = os.getenv("GMAIL_USER")
    app_pw = os.getenv("GMAIL_APP_PASSWORD")
    recipients = [r.strip() for r in os.getenv("GMAIL_TO","").split(",") if r.strip()]
    if not (user and app_pw and recipients):
        print("Gmail env not fully configured; skipping email send.")
        return

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(user, app_pw)
        server.send_message(msg)
        print("Email sent to:", recipients)
