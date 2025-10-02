import requests
import logging
from typing import List, Optional
from requests.exceptions import RequestException, HTTPError, Timeout

from shared_code.models.inverter_power import InverterPower

class DataManager:

    def fetchInverterData(self, url_base: str, site_id: str, inverter_serial: str, token: str, start_datetime: str, end_datetime: str) -> Optional[dict]:
        """Fetch inverter data from SolarEdge API"""
        try:
            url = f"{url_base}/equipment/{site_id}/{inverter_serial}/data"
            parameters = {
                'startTime': start_datetime, 
                'endTime': end_datetime, 
                'api_key': token
            }

            logging.info(f'Fetching inverter data for serial {inverter_serial} from {start_datetime} to {end_datetime}')
            
            response = requests.get(url, params=parameters, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logging.info(f'Successfully fetched data for inverter {inverter_serial}')
            return data
            
        except HTTPError as e:
            logging.error(f'HTTP error fetching inverter data for {inverter_serial}: {e}')
            raise
        except Timeout as e:
            logging.error(f'Timeout fetching inverter data for {inverter_serial}: {e}')
            raise
        except RequestException as e:
            logging.error(f'Request error fetching inverter data for {inverter_serial}: {e}')
            raise
        except Exception as e:
            logging.error(f'Unexpected error fetching inverter data for {inverter_serial}: {e}')
            raise

    def fetchEquipment(self, url_base: str, site_id: str, token: str) -> Optional[dict]:
        """Fetch equipment list from SolarEdge API"""
        try:
            url = f"{url_base}/equipment/{site_id}/list"
            parameters = {'api_key': token}

            logging.info(f'Fetching equipment data for site {site_id}')
            
            response = requests.get(url, params=parameters, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logging.info(f'Successfully fetched equipment data for site {site_id}')
            return data
            
        except HTTPError as e:
            logging.error(f'HTTP error fetching equipment data: {e}')
            raise
        except Timeout as e:
            logging.error(f'Timeout fetching equipment data: {e}')
            raise
        except RequestException as e:
            logging.error(f'Request error fetching equipment data: {e}')
            raise
        except Exception as e:
            logging.error(f'Unexpected error fetching equipment data: {e}')
            raise

    def getInverterSerialNumbers(self, url_base: str, site_id: str, token: str) -> List[str]:
        """Get list of inverter serial numbers from equipment list"""
        try:
            data = self.fetchEquipment(url_base, site_id, token)

            if not data:
                logging.error("No equipment data received from API")
                raise ValueError("No equipment data received from API")

            equipment_list = data.get('reporters', {}).get('list', [])

            if not equipment_list:
                logging.warning("No equipment found in the site")
                return []

            result = []
            for item in equipment_list:
                if item.get('name', '').startswith('Inverter'):
                    serial = item.get('serialNumber')
                    if serial:
                        result.append(serial)
                        logging.info(f'Found inverter with serial: {serial}')

            if not result:
                logging.warning("No inverters found in equipment list")
            else:
                logging.info(f'Found {len(result)} inverters total')

            return result
            
        except Exception as e:
            logging.error(f'Error getting inverter serial numbers: {e}')
            raise

    def getAllInverterPower(self, url_base: str, site_id: str, token: str, start_datetime: str, end_datetime: str) -> List[InverterPower]:
        """Get power data for all inverters in the site"""
        try:
            inverter_serials = self.getInverterSerialNumbers(url_base, site_id, token)

            if not inverter_serials:
                logging.warning("No inverters found to process")
                return []

            result = []
            logging.info(f'Processing {len(inverter_serials)} inverters')

            for serial in inverter_serials:
                try:
                    inverter_data = self.fetchInverterData(url_base, site_id, serial, token, start_datetime, end_datetime)
                    
                    if not inverter_data or 'data' not in inverter_data:
                        logging.warning(f'No data received for inverter {serial}')
                        result.append(InverterPower(serial, 0.0, 0.0))
                        continue

                    all_samples = inverter_data['data'].get('telemetries', [])

                    if not all_samples:
                        logging.warning(f'No telemetry samples found for inverter {serial}')
                        result.append(InverterPower(serial, 0.0, 0.0))
                        continue

                    # Calculate last and average power
                    last_sample = all_samples[-1]
                    last_power = last_sample.get('totalActivePower', 0.0)

                    total_power = sum(sample.get('totalActivePower', 0.0) for sample in all_samples)
                    average_power = total_power / len(all_samples) if all_samples else 0.0

                    logging.info(f'Inverter {serial}: {len(all_samples)} samples, avg={average_power:.1f}W, last={last_power:.1f}W')
                    result.append(InverterPower(serial, average_power, last_power))

                except Exception as e:
                    logging.error(f'Error processing inverter {serial}: {e}')
                    # Add zero power entry for failed inverter to maintain visibility
                    result.append(InverterPower(serial, 0.0, 0.0))
                    continue

            logging.info(f'Successfully processed {len(result)} inverters')
            return result
            
        except Exception as e:
            logging.error(f'Error getting inverter power data: {e}')
            raise