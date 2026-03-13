import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    async def send_email(
            self,
            to_email: str,
            subject: str,
            html_content: str,
            text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add plain text version
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))

            # Add HTML version
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new signup"""
        subject = "Welcome to Superleague Alpha!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .content {{ padding: 30px; background: #f9f9f9; border-radius: 10px; margin-top: 20px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea;
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Superleague!</h1>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Thank you for signing up for early access to Superleague! You're now on the list to be among the first to experience:</p>
                    <ul>
                        <li>✨ Exclusive celebrity interviews</li>
                        <li>🎨 Unique arts and cultural content</li>
                        <li>🎯 Behind-the-scenes access</li>
                    </ul>
                    <p>We'll notify you as soon as we're ready to welcome you. In the meantime, follow us on social media for updates!</p>
                    <a href="https://superleague.com" class="button">Visit Website</a>
                </div>
                <div class="footer">
                    <p>© 2024 Superleague. All rights reserved.</p>
                    <p>You're receiving this because you signed up for early access.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_admin_notification(self, signup_data: dict) -> bool:
        """Notify admin of new signup"""
        subject = "New Alpha Signup!"

        html_content = f"""
        <h2>New Alpha Signup</h2>
        <p><strong>Name:</strong> {signup_data['name']}</p>
        <p><strong>Email:</strong> {signup_data['email']}</p>
        <p><strong>Signed up at:</strong> {signup_data['signed_up_at']}</p>
        """

        return await self.send_email(settings.SMTP_USER, subject, html_content)


# Create global email service
email_service = EmailService()