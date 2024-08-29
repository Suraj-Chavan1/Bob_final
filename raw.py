import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, recipient_email):
    sender_email = "cyberwardensbankofbaroda@gmail.com"
    sender_password = "bkcBKC123"  # Update this with the application-specific password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Authentication error. Check your email and password.")
    except smtplib.SMTPConnectError:
        print("Failed to connect to the server. Check your internet connection or SMTP server settings.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
send_email("Test Subject", "This is the body of the email", "suraj.chavan22@vit.edu")
