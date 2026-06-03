# Audit Entity for NileGov Stack
# Digi-Verse Uganda Limited

import hashlib


class AuditEvent:
    """Represents a secure, historical audit log record for state changes."""
    def __init__(self, event_id: str, request_id: str, operator_id: str, action: str, details: str, prev_hash: str):
        self.event_id = event_id
        self.request_id = request_id
        self.operator_id = operator_id
        self.action = action
        self.details = details
        self.prev_hash = prev_hash
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        payload = f"{self.event_id}{self.request_id}{self.operator_id}{self.action}{self.details}{self.prev_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
