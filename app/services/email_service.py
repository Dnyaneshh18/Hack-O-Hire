"""
Email Service for SAR Export
Sends SAR exports via email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from app.core.config import settings


class EmailService:
    """Service for sending SAR exports via email"""
    
    def __init__(self):
        # Email configuration from settings
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD
        self.email_enabled = settings.EMAIL_ENABLED
    
    def send_sar_export(
        self,
        recipient_email: str,
        case_id: str,
        file_content: bytes,
        file_format: str,
        sender_password: Optional[str] = None
    ) -> dict:
        """
        Send SAR export via email
        
        Args:
            recipient_email: Recipient's email address
            case_id: SAR case ID
            file_content: File content as bytes
            file_format: Format (pdf, xml, csv)
            sender_password: Sender's email password (optional, uses env if not provided)
            
        Returns:
            dict: Status message
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"SAR Export - {case_id}"
            
            # Email body
            body = f"""
Dear Recipient,

Please find attached the Suspicious Activity Report (SAR) export for case {case_id}.

Format: {file_format.upper()}
Exported from: Barclays AML Intelligence Platform
Sender: {self.sender_email}

This is an automated message. Please do not reply to this email.

Best regards,
Barclays AML Compliance Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach file
            filename = f"SAR_{case_id}.{file_format}"
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_content)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(attachment)
            
            # Check if email sending is enabled
            if self.email_enabled and (self.sender_password or sender_password):
                # Send email via SMTP
                password = sender_password or self.sender_password
                
                try:
                    # Create SMTP connection
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                    server.set_debuglevel(0)  # Set to 1 for debugging
                    
                    # Start TLS encryption
                    server.starttls()
                    
                    # Login to email account
                    server.login(self.sender_email, password)
                    
                    # Send email
                    server.send_message(msg)
                    
                    # Close connection
                    server.quit()
                    
                    return {
                        "success": True,
                        "message": f"SAR {case_id} sent successfully to {recipient_email}",
                        "recipient": recipient_email,
                        "format": file_format,
                        "case_id": case_id,
                        "mode": "email_sent"
                    }
                    
                except smtplib.SMTPAuthenticationError as auth_err:
                    error_msg = str(auth_err)
                    return {
                        "success": False,
                        "message": f"Email authentication failed: {error_msg}. Please verify your App Password is correct.",
                        "error": "SMTP Authentication Error",
                        "details": error_msg
                    }
                except smtplib.SMTPException as smtp_err:
                    return {
                        "success": False,
                        "message": f"SMTP error: {str(smtp_err)}",
                        "error": str(smtp_err)
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Connection error: {str(e)}",
                        "error": str(e)
                    }
            else:
                # Demo mode - simulate success
                return {
                    "success": True,
                    "message": f"SAR {case_id} export prepared for {recipient_email} (Demo Mode - Email not sent)",
                    "recipient": recipient_email,
                    "format": file_format,
                    "case_id": case_id,
                    "mode": "demo",
                    "note": "To enable actual email sending, set EMAIL_ENABLED=True and configure SENDER_PASSWORD in .env file"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "error": str(e)
            }
