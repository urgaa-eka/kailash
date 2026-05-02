"""
Email Service for Kailash
Uses AWS SES via SMTP for sending emails
"""

import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

logger = logging.getLogger("kailash.email")


class EmailService:
    """AWS SES Email Service using SMTP"""
    
    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST", "email-smtp.ap-south-1.amazonaws.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_username = os.environ.get("SMTP_USERNAME")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("SMTP_FROM_EMAIL", "noreply@kailash-ai.in")
        self.from_name = os.environ.get("SMTP_FROM_NAME", "KAILASH AI")
        self.frontend_url = os.environ.get("FRONTEND_URL", "https://kailash-ai.in")
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured. SMTP_USERNAME or SMTP_PASSWORD missing.")
    
    def _create_reset_email_html(self, reset_link: str, user_name: str = "User") -> str:
        """Create HTML email template for password reset"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - KAILASH AI</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Inter', Arial, sans-serif; background-color: #0a0a1a;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a1a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%); border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.3);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px; text-align: center; border-bottom: 1px solid rgba(129, 114, 173, 0.2);">
                                    <h1 style="margin: 0; font-size: 32px; font-weight: 700; background: linear-gradient(90deg, #8172AD, #4CAF50, #DF8C4D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Kailash</h1>
                                    <p style="margin: 8px 0 0; color: #8172AD; font-size: 14px; letter-spacing: 2px;">KAILASH "THE DEVINE AI"</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 16px; color: #ffffff; font-size: 24px; font-weight: 600;">Password Reset Request</h2>
                                    <p style="margin: 0 0 24px; color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                        Hello {user_name},
                                    </p>
                                    <p style="margin: 0 0 24px; color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                        We received a request to reset your password for your Kailash account. Click the button below to create a new password:
                                    </p>
                                    
                                    <!-- CTA Button -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" style="padding: 20px 0;">
                                                <a href="{reset_link}" style="display: inline-block; padding: 16px 40px; background: linear-gradient(90deg, #8172AD, #4CAF50); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 8px; box-shadow: 0 4px 16px rgba(129, 114, 173, 0.3);">
                                                    Reset Password
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 24px 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                        This link will expire in <strong style="color: #DF8C4D;">1 hour</strong> for security reasons.
                                    </p>
                                    <p style="margin: 16px 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                        If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.
                                    </p>
                                    
                                    <!-- Link fallback -->
                                    <div style="margin-top: 32px; padding: 20px; background: rgba(129, 114, 173, 0.1); border-radius: 8px; border: 1px solid rgba(129, 114, 173, 0.2);">
                                        <p style="margin: 0 0 8px; color: #a0a0a0; font-size: 12px;">
                                            If the button doesn't work, copy and paste this link:
                                        </p>
                                        <p style="margin: 0; color: #8172AD; font-size: 12px; word-break: break-all;">
                                            {reset_link}
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 24px 40px; background: rgba(0,0,0,0.2); border-top: 1px solid rgba(129, 114, 173, 0.2);">
                                    <p style="margin: 0; color: #666666; font-size: 12px; text-align: center;">
                                        Go4Garage EV Charging Network | URGAA EV Charging
                                    </p>
                                    <p style="margin: 8px 0 0; color: #666666; font-size: 12px; text-align: center;">
                                        © 2025 KAILASH AI. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    
    def _create_reset_email_text(self, reset_link: str, user_name: str = "User") -> str:
        """Create plain text email for password reset"""
        return f"""
Kailash - Password Reset

Hello {user_name},

We received a request to reset your password for your Kailash account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.

---
Go4Garage EV Charging Network | URGAA EV Charging
© 2025 KAILASH AI. All rights reserved.
        """
    
    async def send_password_reset_email(
        self, 
        to_email: str, 
        reset_token: str, 
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            reset_token: The password reset token
            user_name: Optional user name for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email not configured. Would send reset email to: {to_email}")
            # Return True in dev to not block the flow
            return True
        
        try:
            # Build reset link
            reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Password Reset - Kailash"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create both plain text and HTML versions
            text_content = self._create_reset_email_text(reset_link, user_name or "User")
            html_content = self._create_reset_email_html(reset_link, user_name or "User")
            
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email via SMTP
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Password reset email sent successfully to: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        if not self.is_configured:
            logger.warning(f"Email not configured. Would send welcome email to: {to_email}")
            return True
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to KAILASH AI</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #0a0a1a;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a1a; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background: #1a1a2e; border-radius: 16px; padding: 40px;">
                                <tr>
                                    <td style="text-align: center;">
                                        <h1 style="color: #8172AD; margin: 0;">Welcome to Kailash!</h1>
                                        <p style="color: #ffffff; font-size: 18px; margin-top: 20px;">Hello {user_name},</p>
                                        <p style="color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                            Your account has been successfully created. You now have access to KAILASH "THE DEVINE AI" - India's most advanced EV charging network management platform.
                                        </p>
                                        <a href="{self.frontend_url}" style="display: inline-block; margin-top: 24px; padding: 16px 40px; background: linear-gradient(90deg, #8172AD, #4CAF50); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600;">
                                            Go to Dashboard
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Welcome to Kailash"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            message.attach(MIMEText(html_content, "html"))
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Welcome email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
