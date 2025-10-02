from datetime import datetime
import logging
from shared_code.services.orchestrator_service import OrchestratorService

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    date = req.params.get('date')
    service = OrchestratorService()
    result = service.checkInverterPower(
        datetime.strptime(date, '%Y-%m-%d'))

    return func.HttpResponse(
        result,
        status_code=200
    )
