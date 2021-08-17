import requests
import logging
import sys

from shared_code.models.inverter_power import InverterPower

class DataManager:

    def fetchInverterData(self, url_base, site_id, inverter_serial, token, start_datetime, end_datetime):
        data = '{}'
        url = url_base + '/equipment/' + site_id + '/' + inverter_serial + '/data'

        parameters = {
            'startTime': start_datetime, 
            'endTime': end_datetime, 
            'api_key': token } 

        try:
            logging.info('Fetching inverter data')
            data = requests.get(url, params=parameters)
            data.raise_for_status()
            return data.json()
        except:
            logging.error('Unable to retrieve data', sys.exc_info()[0])
            return data

    def fetchEqupment(self, url_base, site_id, token):
        data = '{}'
        url = url_base + '/equipment/' + site_id + '/list'

        parameters = {
            'api_key': token } 

        try:
            logging.info('Fetching equipment data')
            data = requests.get(url, params=parameters)
            data.raise_for_status()
            return data.json()
        except:
            logging.error('Unable to retrieve data', sys.exc_info()[0])
            return data

    def getInverterSerialNumbers(self, url_base, site_id, token):
        data = self.fetchEqupment(url_base, site_id, token)

        if(data is None):
            raise ValueError(data)

        equpment = data['reporters']['list']

        if(equpment is None or len(equpment) == 0):
            raise ValueError(equpment)

        result = []

        for item in equpment:
            if(item['name'].startswith('Inverter')):
                result.append(item['serialNumber'])

        return result

    def getAllInverterPower(self, url_base, site_id, token, start_datetime, end_datetime):
        inverterSerials = self.getInverterSerialNumbers(url_base, site_id, token)

        if(inverterSerials is None or len(inverterSerials) == 0):
            raise ValueError(inverterSerials)

        result = []

        for serial in inverterSerials:
            inverter_data = self.fetchInverterData(url_base, site_id, serial, token, start_datetime, end_datetime) 

            try:
                all_samples = inverter_data['data']['telemetries']

                if(all_samples is None or len(all_samples) == 0):
                    raise ValueError(all_samples)

                last_sample = all_samples[-1]

                if(last_sample is None):
                    raise ValueError(last_sample)

                last_power = last_sample['totalActivePower']

                total_power = 0

                for sample in all_samples:
                    total_power += sample['totalActivePower']

                average_power = total_power / len(all_samples)

                result.append(InverterPower(serial, average_power, last_power))

            except:
                logging.error('Unable to retrieve data', sys.exc_info()[0])

        return result