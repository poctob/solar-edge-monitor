import datetime
import os

from shared_code.services.data_manager import DataManager
from shared_code.services.email_manager import EmailManager


class OrchestratorService:
    def checkInverterPower(self, date):

        if(date is None):
            today = datetime.date.today()
        else:
            today = date
            
        today_start = f'{today.year}-{today.month}-{today.day} 12:00:00'
        today_end = f'{today.year}-{today.month}-{today.day} 12:59:59'

        alert_value = float(os.environ["alertPowerThreshold"])

        dataManager = DataManager()
        email = EmailManager()

        inverter_data = dataManager.getAllInverterPower(
            os.environ["baseURL"],
            os.environ["siteId"],
            os.environ["solarEdgeApiKey"],
            today_start,
            today_end)

        result = ''

        for inverter_power in inverter_data:
            result += f'''For serial {inverter_power.serial}:
            last sample generated power is {inverter_power.last} Watts
            average generated power {inverter_power.average} Watts'''

            if(inverter_power.last < alert_value or inverter_power.average < alert_value):
                email.sendAlertEmail(
                    os.environ["sendGridApiKey"],
                    os.environ["toEmail"],
                    os.environ["fromEmail"],
                    inverter_power.serial)

        return result