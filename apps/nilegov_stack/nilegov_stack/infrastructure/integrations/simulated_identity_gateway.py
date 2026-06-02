# Simulated Identity Verification Gateway
# Digi-Verse Uganda Limited

from nilegov_stack.application.ports import IdentityVerificationGateway


class SimulatedIdentityVerificationGateway(IdentityVerificationGateway):
    """Simulated NIRA Identity Verification Gateway adapter.
    
    Contains disclaimers indicating it is a prototype mock and not connected to NIRA.
    """
    DISCLAIMER = "Prototype simulation only. No live Government registry access."

    def verify_identity(self, nin: str) -> dict:
        # Standard Uganda demo NIN check
        clean_nin = nin.strip().upper()
        
        # Scenario matching:
        # If NIN starts with CF90, it is our designated demo user
        if clean_nin == "CF900000000000" or clean_nin == "CF123456789012":
            return {
                "success": True,
                "result": "Matched",
                "message": "NIRA Simulated Identity Verified: Citizen match found.",
                "citizen_name": "Robert Sebunya",
                "location": "Ntinda, Kampala",
                "disclaimer": self.DISCLAIMER
            }
        elif clean_nin.startswith("CF8"):
            return {
                "success": False,
                "result": "Requires Review",
                "message": "Simulated Registry Check: Fingerprint verification required.",
                "disclaimer": self.DISCLAIMER
            }
        else:
            return {
                "success": False,
                "result": "Not Matched",
                "message": "Simulated Registry Check: No matching citizen NIN found.",
                "disclaimer": self.DISCLAIMER
            }
