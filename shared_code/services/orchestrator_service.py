import datetime
import os
import logging
from typing import Optional

from shared_code.services.data_manager import DataManager
from shared_code.services.email_manager import EmailManager


class OrchestratorService:
    def checkInverterPower(self, date: Optional[datetime.date] = None) -> str:
        """
        Check inverter power output and send alerts if below threshold
        
        Args:
            date: Date to check (defaults to today)
            
        Returns:
            String summary of results
        """
        try:
            # Determine date to check
            if date is None:
                today = datetime.date.today()
            else:
                today = date

            logging.info(f'Checking inverter power for date: {today}')

            # Define time window (12 PM to 1 PM)
            today_start = f'{today.year}-{today.month:02d}-{today.day:02d} 12:00:00'
            today_end = f'{today.year}-{today.month:02d}-{today.day:02d} 12:59:59'

            # Get configuration values
            try:
                alert_value = float(os.environ.get("alertPowerThreshold", "200"))
                base_url = os.environ.get("baseURL", "")
                site_id = os.environ.get("siteId", "")
                api_key = os.environ.get("solarEdgeApiKey", "")
                sendgrid_key = os.environ.get("sendGridApiKey", "")
                to_email = os.environ.get("toEmail", "")
                from_email = os.environ.get("fromEmail", "")
                
                # Validate required configuration
                if not all([base_url, site_id, api_key]):
                    raise ValueError("Missing required SolarEdge configuration (baseURL, siteId, solarEdgeApiKey)")
                
                logging.info(f'Configuration: threshold={alert_value}W, site={site_id}, time_window={today_start} to {today_end}')
                
            except (ValueError, KeyError) as e:
                logging.error(f'Configuration error: {e}')
                return f'Configuration error: {e}'

            # Initialize services
            data_manager = DataManager()
            email_manager = EmailManager()

            # Fetch inverter data
            try:
                inverter_data = data_manager.getAllInverterPower(
                    base_url, site_id, api_key, today_start, today_end)
                
                if not inverter_data:
                    logging.warning('No inverter data received')
                    return 'No inverter data available for the specified time period'
                    
            except Exception as e:
                logging.error(f'Failed to fetch inverter data: {e}')
                return f'Failed to fetch inverter data: {e}'

            # Process results and send alerts
            result_lines = []
            alerts_sent = 0
            
            for inverter_power in inverter_data:
                serial = inverter_power.serial
                last_power = inverter_power.last
                average_power = inverter_power.average
                
                result_line = f'Inverter {serial}: last={last_power:.1f}W, average={average_power:.1f}W'
                result_lines.append(result_line)
                
                # Check if alert needed
                needs_alert = last_power < alert_value or average_power < alert_value
                
                if needs_alert:
                    logging.warning(f'Alert condition met for inverter {serial}: last={last_power}W, avg={average_power}W, threshold={alert_value}W')
                    
                    # Send alert email if email is configured
                    if sendgrid_key and to_email and from_email:
                        try:
                            email_manager.sendAlertEmail(sendgrid_key, to_email, from_email, serial)
                            alerts_sent += 1
                            result_lines.append(f'  → Alert sent for {serial}')
                        except Exception as e:
                            logging.error(f'Failed to send alert email for {serial}: {e}')
                            result_lines.append(f'  → Alert failed for {serial}: {e}')
                    else:
                        logging.warning(f'Email not configured - alert not sent for {serial}')
                        result_lines.append(f'  → Alert needed for {serial} but email not configured')
                else:
                    logging.info(f'Inverter {serial} operating normally')

            # Create summary
            summary = f'Checked {len(inverter_data)} inverters on {today}, sent {alerts_sent} alerts\n' + '\n'.join(result_lines)
            logging.info(f'Check complete: {len(inverter_data)} inverters, {alerts_sent} alerts sent')
            
            return summary

        except Exception as e:
            error_msg = f'Unexpected error during inverter check: {e}'
            logging.error(error_msg)
            return error_msg