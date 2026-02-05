"""
Email Notification Sender for Notification Service.

Sends email notifications using SMTP with configuration from Dapr Secrets API.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

from ...shared.dapr_client.client import DaprClientWrapper
from ..config.secrets import SecretsManager

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Service for sending email notifications.

    Uses SMTP to send email reminders to users.
    Configuration retrieved from Dapr Secrets API.
    """

    def __init__(self):
        """Initialize email notifier."""
        self.dapr_client = DaprClientWrapper()
        self.secrets_manager = SecretsManager()

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        task_id: str,
        reminder_type: str
    ) -> Dict[str, Any]:
        """
        Send an email notification.

        Args:
            user_id: ID of the user
            title: Email subject
            body: Email body text
            task_id: ID of the related task
            reminder_type: Type of reminder (advance/due)

        Returns:
            Dict with success status
        """
        try:
            # Get user email from preferences
            user_email = await self._get_user_email(user_id)
            if not user_email:
                logger.warning(f"No email address found for user {user_id}")
                return {
                    "success": False,
                    "message": "User email address not found"
                }

            # Get SMTP configuration from secrets
            smtp_config = await self.secrets_manager.get_smtp_config()
            if not smtp_config:
                logger.error("SMTP configuration not available")
                return {
                    "success": False,
                    "message": "Email service not configured"
                }

            # Create email message
            message = self._create_email_message(
                to_email=user_email,
                subject=title,
                body=body,
                task_id=task_id,
                reminder_type=reminder_type,
                from_email=smtp_config.get("from_email", "noreply@todo-chatbot.com")
            )

            # Send email via SMTP
            result = await self._send_email_smtp(message, smtp_config)

            if result["success"]:
                # Log successful delivery
                await self._log_email_delivery(
                    user_id=user_id,
                    task_id=task_id,
                    email=user_email,
                    status="sent"
                )

                logger.info(f"Email notification sent to {user_email}")

                return {
                    "success": True,
                    "message": "Email notification sent successfully"
                }
            else:
                # Log failed delivery
                await self._log_email_delivery(
                    user_id=user_id,
                    task_id=task_id,
                    email=user_email,
                    status="failed",
                    error=result.get("error")
                )

                return result

        except Exception as e:
            logger.error(f"Error sending email notification: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send email notification: {str(e)}"
            }

    def _create_email_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        task_id: str,
        reminder_type: str,
        from_email: str
    ) -> MIMEMultipart:
        """
        Create email message with HTML and plain text versions.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            task_id: Task ID
            reminder_type: Reminder type
            from_email: Sender email address

        Returns:
            MIMEMultipart message
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = to_email

        # Plain text version
        text_content = f"{body}\n\nTask ID: {task_id}\n"

        # HTML version
        html_content = f"""
        <html>
          <body>
            <h2>{subject}</h2>
            <p>{body.replace(chr(10), '<br>')}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
              Task ID: {task_id}<br>
              Reminder Type: {reminder_type}
            </p>
          </body>
        </html>
        """

        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        message.attach(part1)
        message.attach(part2)

        return message

    async def _send_email_smtp(
        self,
        message: MIMEMultipart,
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send email via SMTP.

        Args:
            message: Email message to send
            smtp_config: SMTP configuration

        Returns:
            Dict with success status
        """
        try:
            smtp_host = smtp_config.get("host", "localhost")
            smtp_port = smtp_config.get("port", 587)
            smtp_user = smtp_config.get("username")
            smtp_password = smtp_config.get("password")
            use_tls = smtp_config.get("use_tls", True)

            # Connect to SMTP server
            if use_tls:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            # Login if credentials provided
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            # Send email
            server.send_message(message)
            server.quit()

            return {
                "success": True,
                "message": "Email sent successfully"
            }

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """
        Get user email address from preferences.

        Args:
            user_id: ID of the user

        Returns:
            Email address or None
        """
        try:
            preferences_key = f"chat-api.preferences.user.{user_id}"
            preferences = await self.dapr_client.get_state(preferences_key)

            if preferences:
                return preferences.get("emailAddress")

            return None

        except Exception as e:
            logger.warning(f"Error getting user email: {e}")
            return None

    async def _log_email_delivery(
        self,
        user_id: str,
        task_id: str,
        email: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """
        Log email delivery attempt.

        Args:
            user_id: ID of the user
            task_id: ID of the task
            email: Email address
            status: Delivery status (sent/failed)
            error: Error message if failed
        """
        try:
            log_entry = {
                "userId": user_id,
                "taskId": task_id,
                "email": email,
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            if error:
                log_entry["error"] = error

            # Store delivery log
            log_key = f"notification.email.log.{user_id}.{task_id}.{datetime.utcnow().timestamp()}"
            await self.dapr_client.save_state(log_key, log_entry)

        except Exception as e:
            logger.warning(f"Error logging email delivery: {e}")
