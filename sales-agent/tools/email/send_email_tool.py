import smtplib
from email.message import EmailMessage
from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from config.config import config


class SendEmailSchema(BaseModel):
    """Schema for sending email"""
    to: str = Field(
        ...,
        description="Email address of the recipient"
    )
    subject: str = Field(
        ...,
        description="Subject line of the email"
    )
    body: str = Field(
        ...,
        description="Email body content. Should be personalized and relevant."
    )


class SendEmailTool(BaseTool):
    """
    Email Sending Tool for outreach campaigns

    Sends personalized emails to prospects with proper formatting
    and signature inclusion.
    """

    name = "send_email"
    description = (
        "Send a personalized email to a prospect. "
        "Use this after researching the company and crafting a relevant message. "
        "The email should be professional, concise, and include a clear call-to-action."
    )
    args_schema = SendEmailSchema

    def execute(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send an email to a prospect

        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content

        Returns:
            Dictionary with success status and message
        """
        # Validate configuration
        if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
            return {
                "success": False,
                "message": "Email credentials not configured",
                "error": "Missing EMAIL_ADDRESS or EMAIL_PASSWORD in configuration"
            }

        try:
            # Create email message
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = config.EMAIL_ADDRESS
            message["To"] = to

            # Add signature if configured
            email_body = body.replace('\\n', '\n')
            if config.EMAIL_SIGNATURE:
                email_body += f"\n\n{config.EMAIL_SIGNATURE}"

            message.set_content(email_body)

            # Send email via SMTP
            with smtplib.SMTP(config.EMAIL_SMTP_HOST, config.EMAIL_SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                smtp.send_message(message)

            return {
                "success": True,
                "message": f"Email successfully sent to {to}",
                "recipient": to,
                "subject": subject
            }

        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Email authentication failed",
                "error": "Invalid email credentials"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message": f"SMTP error: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "error": str(e)
            }
