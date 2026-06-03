# Use case: Register Pesapal IPN URL
# Digi-Verse Uganda Limited

from nilegov_stack.infrastructure.integrations.pesapal_api_client import PesapalApiClient, PesapalIPNRegistrationResult


class RegisterPesapalIPN:
    """Application Service to register the configured IPN URL with Pesapal API 3.0."""

    def __init__(self, api_client: PesapalApiClient):
        self.api_client = api_client

    def execute(self) -> PesapalIPNRegistrationResult:
        auth_token = self.api_client.request_token()
        result = self.api_client.register_ipn_url(auth_token.token)
        return result
