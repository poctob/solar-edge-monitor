import sendgrid
import logging
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional

class EmailManager:

    def sendAlertEmail(self, api_key: str, to: str, from_email: str, serial: str) -> Optional[dict]:
        """Send alert email via SendGrid"""
        try:
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            
            from_email_obj = Email(from_email)
            to_email_obj = To(to)
            subject = "🔴 SolarEdge Power Alert"
            
            content_text = f"""
SolarEdge Power Generation Alert

Your solar inverter power generation is outside of acceptable parameters.

Inverter Details:
- Serial Number: {serial}
- Alert Time: Please check the monitoring portal for exact timing

Next Steps:
1. Login to your SolarEdge portal to review generation data
2. Check for any system maintenance notifications
3. Contact your installer if the issue persists

This is an automated alert from your solar monitoring system.
            """.strip()
            
            content = Content("text/plain", content_text)
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            
            logging.info(f'Sending alert email for inverter {serial} to {to}')
            response = sg.send(mail)
            
            if response.status_code == 202:
                logging.info(f'Alert email sent successfully for inverter {serial}')
            else:
                logging.warning(f'Email sent with status code {response.status_code} for inverter {serial}')
                
            return {
                'status_code': response.status_code,
                'body': response.body,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            logging.error(f'Failed to send alert email for inverter {serial}: {e}')
            raise
