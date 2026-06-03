"""Use cases for recording simulated integration outcomes."""


class RecordIntegrationSuccess:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, integration_request_id: str, response_payload: dict):
        request = self.repository.get(integration_request_id)
        if request is None:
            raise ValueError("Integration request not found")
        response = request.mark_success(response_payload)
        self.repository.save(request)
        return response


class RecordIntegrationFailure:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, integration_request_id: str, error_code: str, error_message: str):
        request = self.repository.get(integration_request_id)
        if request is None:
            raise ValueError("Integration request not found")
        response = request.mark_failure(error_code, error_message)
        self.repository.save(request)
        return response
