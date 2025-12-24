"""
Alert and Notification System

Monitors transport conditions and sends alerts for:
- Severe congestion
- Unusual delays
- System anomalies

Supports multiple notification channels:
- In-app notifications (via API)
- Email notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
from database import get_database
from analytics import get_analytics

load_dotenv()

# Email configuration (optional)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")


class AlertManager:
    """Manages congestion alerts and notifications"""

    # Alert severity levels
    SEVERITY_INFO = "INFO"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_CRITICAL = "CRITICAL"

    # Alert types
    TYPE_SEVERE_CONGESTION = "SEVERE_CONGESTION"
    TYPE_UNUSUAL_DELAY = "UNUSUAL_DELAY"
    TYPE_HIGH_LSD_RATIO = "HIGH_LSD_RATIO"
    TYPE_SYSTEM_ANOMALY = "SYSTEM_ANOMALY"

    def __init__(self):
        """Initialize alert manager"""
        self.db = get_database()
        self.analytics = get_analytics()
        self.email_enabled = bool(SMTP_USER and SMTP_PASSWORD and ALERT_EMAIL_TO)

        if self.email_enabled:
            print(f"✓ Email alerts enabled: {ALERT_EMAIL_TO}")
        else:
            print("⚠ Email alerts disabled (configure SMTP settings in .env)")

    def check_and_create_alerts(self) -> List[Dict]:
        """
        Check current conditions and create alerts if needed

        Returns:
            List of new alerts created
        """
        new_alerts = []

        # Check for severe congestion
        comparison = self.analytics.get_current_vs_historical(hours=24)

        if "error" not in comparison:
            congestion_level = comparison['comparison']['congestion_level']
            delay_change = comparison['comparison']['delay_change_percent']
            current_stats = comparison['current_stats']

            # Severe congestion alert
            if congestion_level == "SEVERE":
                alert = self._create_alert(
                    alert_type=self.TYPE_SEVERE_CONGESTION,
                    severity=self.SEVERITY_CRITICAL,
                    message=f"Severe congestion detected across the network",
                    details={
                        "avg_delay": current_stats['avg_delay'],
                        "severe_delays": current_stats['severe_delays'],
                        "lsd_count": current_stats['load_distribution']['LSD']
                    }
                )
                new_alerts.append(alert)

            # Unusual delay alert
            elif congestion_level == "HIGH" and delay_change > 50:
                alert = self._create_alert(
                    alert_type=self.TYPE_UNUSUAL_DELAY,
                    severity=self.SEVERITY_WARNING,
                    message=f"Traffic delays are {delay_change:.0f}% higher than usual",
                    details={
                        "delay_change_percent": delay_change,
                        "current_avg_delay": current_stats['avg_delay']
                    }
                )
                new_alerts.append(alert)

            # High LSD ratio alert
            lsd_ratio = current_stats['load_distribution']['LSD'] / current_stats['total_buses']
            if lsd_ratio > 0.4:  # More than 40% buses are crowded
                alert = self._create_alert(
                    alert_type=self.TYPE_HIGH_LSD_RATIO,
                    severity=self.SEVERITY_WARNING,
                    message=f"{lsd_ratio*100:.0f}% of buses are severely crowded",
                    details={
                        "lsd_ratio": lsd_ratio,
                        "lsd_count": current_stats['load_distribution']['LSD'],
                        "total_buses": current_stats['total_buses']
                    }
                )
                new_alerts.append(alert)

        # Send notifications for new alerts
        for alert in new_alerts:
            self._send_notifications(alert)

        return new_alerts

    def _create_alert(self, alert_type: str, severity: str,
                     message: str, details: Dict,
                     bus_stop_code: str = None, bus_number: str = None) -> Dict:
        """Create and store an alert"""
        alert_data = {
            "alert_type": alert_type,
            "severity": severity,
            "bus_stop_code": bus_stop_code,
            "bus_number": bus_number,
            "message": message,
            "details": details
        }

        alert_id = self.db.insert_alert(alert_data)
        alert_data['id'] = alert_id
        alert_data['created_at'] = datetime.now().isoformat()

        print(f"🚨 Alert created: [{severity}] {message}")

        return alert_data

    def _send_notifications(self, alert: Dict):
        """Send notifications for an alert (email + mark for in-app)"""
        # Send email notification
        if self.email_enabled and alert['severity'] in [self.SEVERITY_CRITICAL, self.SEVERITY_WARNING]:
            self._send_email_alert(alert)

        # Mark as available for in-app notification (will be picked up by API)
        # In-app notifications are handled by the frontend polling the alerts endpoint
        pass

    def _send_email_alert(self, alert: Dict):
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = ALERT_EMAIL_TO
            msg['Subject'] = f"[{alert['severity']}] Singapore Transport Alert"

            # Email body
            body = f"""
Singapore Transport Intelligence Alert

Alert Type: {alert['alert_type']}
Severity: {alert['severity']}
Time: {alert.get('created_at', datetime.now().isoformat())}

Message:
{alert['message']}

Details:
{self._format_details(alert['details'])}

---
This is an automated alert from Singapore Transport Intelligence Dashboard.
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            print(f"📧 Email alert sent to {ALERT_EMAIL_TO}")

            # Mark as notified
            self.db.mark_alert_notified(alert['id'])

        except Exception as e:
            print(f"✗ Error sending email alert: {e}")

    def _format_details(self, details: Dict) -> str:
        """Format alert details for email"""
        lines = []
        for key, value in details.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"  - {formatted_key}: {value}")
        return '\n'.join(lines)

    def get_active_alerts(self, severity: str = None) -> List[Dict]:
        """Get currently active alerts"""
        return self.db.get_active_alerts(severity=severity)

    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        self.db.resolve_alert(alert_id)
        print(f"✓ Alert {alert_id} resolved")

    def auto_resolve_old_alerts(self, hours: int = 2):
        """
        Automatically resolve alerts older than specified hours

        Args:
            hours: Hours after which alerts are auto-resolved
        """
        active_alerts = self.get_active_alerts()

        for alert in active_alerts:
            created_at = datetime.fromisoformat(alert['created_at'])
            age = datetime.now() - created_at

            if age.total_seconds() > hours * 3600:
                self.resolve_alert(alert['id'])


# Singleton instance
_alert_manager_instance = None


def get_alert_manager() -> AlertManager:
    """Get singleton alert manager instance"""
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager()
    return _alert_manager_instance


if __name__ == "__main__":
    # Test alert system
    print("Testing Alert System...")

    manager = get_alert_manager()

    print("\nChecking for alerts...")
    alerts = manager.check_and_create_alerts()

    print(f"\nCreated {len(alerts)} new alerts")

    print("\nActive alerts:")
    active = manager.get_active_alerts()
    for alert in active:
        print(f"  [{alert['severity']}] {alert['message']}")

    print("\nAuto-resolving old alerts...")
    manager.auto_resolve_old_alerts(hours=2)
