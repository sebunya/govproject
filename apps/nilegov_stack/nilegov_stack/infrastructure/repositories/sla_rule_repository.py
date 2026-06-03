# InMemory SLA Rule Repository Implementation
# Prototype simulation only. No live Government registry access.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import SLARuleRepository
from nilegov_stack.domain.sla import SLARule

class InMemorySLARuleRepository(SLARuleRepository):
    """In-memory implementation of the SLARuleRepository port for local tests."""
    def __init__(self):
        self._rules: Dict[str, SLARule] = {}

    def save(self, rule: SLARule) -> None:
        self._rules[rule.rule_id] = rule

    def get_by_id(self, rule_id: str) -> Optional[SLARule]:
        return self._rules.get(rule_id)

    def get_by_service_type(self, service_type: str) -> Optional[SLARule]:
        for rule in self._rules.values():
            if rule.service_type == service_type and rule.active:
                return rule
        return None

    def get_all(self) -> List[SLARule]:
        return list(self._rules.values())
