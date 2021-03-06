import datetime
import logging
from shared_code.services.orchestrator_service import OrchestratorService

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    service = OrchestratorService()
    result = service.checkInverterPower(None)
    logging.info(result)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
