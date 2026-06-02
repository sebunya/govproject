"""List simulated integration requests."""


class ListIntegrationRequests:
    def __init__(self, repository):
        self.repository = repository

    def by_target_system(self, target_system: str):
        return self.repository.list_by_target_system(target_system)

    def by_status(self, status: str):
        return self.repository.list_by_status(status)

    def by_service_request(self, service_request_reference: str):
        return self.repository.list_by_service_request(service_request_reference)

    def all(self):
        return self.repository.list_all()
