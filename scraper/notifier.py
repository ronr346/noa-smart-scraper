"""
Notification system — send alerts via Email and Telegram.

The Notifier class supports multiple notification channels
and includes change detection to avoid duplicate alerts.
"""

import os
import smtplib
import hashlib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class Notifier:
    """
    Send notifications through multiple channels.
    
    Supports:
    - Email (SMTP)
    - Telegram Bot API
    - Console (for testing)
    
    Usage:
        notifier = Notifier()
        notifier.send("Price dropped to $99!", channels=["email", "telegram"])
    """
    
    def __init__(self):
        """Initialize notifier with environment-based configuration."""
        self._previous_hashes = {}  # Track content hashes for change detection
        
        # Email config
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.notify_email = os.getenv("NOTIFY_EMAIL")
        
        # Telegram config
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def send(self, message, subject="Smart Scraper Alert", channels=None):
        """
        Send a notification through specified channels.
        
        Args:
            message: Notification text
            subject: Email subject line
            channels: List of channels ("email", "telegram", "console")
                      Default: ["console"]
        """
        if channels is None:
            channels = ["console"]
        
        for channel in channels:
            try:
                if channel == "email":
                    self._send_email(subject, message)
                elif channel == "telegram":
                    self._send_telegram(message)
                elif channel == "console":
                    self._send_console(message)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to send via {channel}: {str(e)}")
    
    def has_changed(self, job_name, content):
        """
        Check if content has changed since the last check.
        
        Uses SHA-256 hashing to efficiently detect changes
        without storing the full content.
        
        Args:
            job_name: Identifier for the scraping job
            content: Current content to compare
            
        Returns:
            True if content has changed (or first check), False otherwise
        """
        content_hash = hashlib.sha256(str(content).encode()).hexdigest()
        previous_hash = self._previous_hashes.get(job_name)
        
        self._previous_hashes[job_name] = content_hash
        
        if previous_hash is None:
            logger.info(f"First check for '{job_name}' — setting baseline")
            return True  # First check always counts as "changed"
        
        changed = content_hash != previous_hash
        if changed:
            logger.info(f"Change detected for '{job_name}'")
        else:
            logger.debug(f"No change for '{job_name}'")
        
        return changed
    
    def _send_email(self, subject, body):
        """
        Send an email notification via SMTP.
        
        Requires SMTP_USER, SMTP_PASSWORD, and NOTIFY_EMAIL
        environment variables to be set.
        """
        if not all([self.smtp_user, self.smtp_password, self.notify_email]):
            logger.error("Email configuration incomplete. Set SMTP_USER, SMTP_PASSWORD, NOTIFY_EMAIL")
            return
        
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = self.notify_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent to {self.notify_email}")
    
    def _send_telegram(self, message):
        """
        Send a Telegram message via Bot API.
        
        Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
        environment variables to be set.
        """
        if not all([self.telegram_token, self.telegram_chat_id]):
            logger.error("Telegram configuration incomplete. Set TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
            return
        
        import requests
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Telegram message sent to chat {self.telegram_chat_id}")
    
    def _send_console(self, message):
        """Print notification to console (for testing and debugging)."""
        print(f"\n{'='*50}")
        print(f"🔔 NOTIFICATION")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")
