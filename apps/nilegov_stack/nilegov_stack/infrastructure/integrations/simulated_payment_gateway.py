# Simulated Payment Verification Gateway
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import PaymentVerificationGateway


class SimulatedPaymentVerificationGateway(PaymentVerificationGateway):
    """Simulated Payment Verification Gateway adapter.
    
    Contains disclaimers indicating it is a mock simulation and not connected to live URA or mobile money.
    """
    DISCLAIMER = "Prototype simulation only. No live payment was processed."

    def verify_payment(self, reference_no: str) -> dict:
        # Returns simulated payment results
        clean_ref = reference_no.strip().upper()
        
        # Standard mock payment: verify any NGS-NIRA reference
        if clean_ref.startswith("NGS-NIRA-2026-"):
            return {
                "success": True,
                "status": "Verified",
                "amount": 50000.0,
                "message": "Simulated Payment Verification: Reference payment verified successfully.",
                "disclaimer": self.DISCLAIMER
            }
        else:
            return {
                "success": False,
                "status": "Failed",
                "amount": 0.0,
                "message": "Simulated Payment Verification: No payment found for the provided reference.",
                "disclaimer": self.DISCLAIMER
            }

    def verify_payment_record(self, payment_record) -> dict:
        """Verifies a PaymentRecord aggregate deterministically.
        
        Never processes real money, never requires credentials, and never calls external APIs.
        """
        ref = payment_record.simulated_transaction_reference.strip().upper()

        if "FAIL" in ref:
            return {
                "success": False,
                "status": "Simulated Failed",
                "amount": 0.0,
                "message": "Simulated Payment Verification: Reference payment failed verification check.",
                "disclaimer": self.DISCLAIMER
            }
        elif "REVIEW" in ref:
            return {
                "success": True,
                "status": "Requires Review",
                "amount": payment_record.amount,
                "message": "Simulated Payment Verification: Payment matches check but requires administrative review.",
                "disclaimer": self.DISCLAIMER
            }

        # Otherwise verify if reference matches
        if ref.startswith("SIM-PAY-") or ref.startswith("NGS-NIRA-") or ref != "":
            return {
                "success": True,
                "status": "Simulated Verified",
                "amount": payment_record.amount,
                "message": "Simulated Payment Verification: Payment verified successfully.",
                "disclaimer": self.DISCLAIMER
            }
        else:
            return {
                "success": False,
                "status": "Simulated Failed",
                "amount": 0.0,
                "message": "Simulated Payment Verification: Invalid reference format.",
                "disclaimer": self.DISCLAIMER
            }
