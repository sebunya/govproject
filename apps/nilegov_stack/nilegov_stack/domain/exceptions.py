# Custom Domain Exceptions for NileGov Stack
# Digi-Verse Uganda Limited

class DomainException(Exception):
    """Base exception for all domain logic rules."""
    pass


class InvalidNINException(DomainException):
    """Raised when a National Identification Number (NIN) format or checksum fails validity tests."""
    pass


class WorkflowTransitionException(DomainException):
    """Raised when an invalid status transition is requested within the Service Request workflow."""
    pass


class ConsentRequiredException(DomainException):
    """Raised when a citizen action is attempted without verification of legal consent."""
    pass
