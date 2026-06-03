# InMemory Reporting Snapshot Repository Implementation
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import ReportingSnapshotRepository
from nilegov_stack.domain.reporting_snapshot import ReportingSnapshot


class InMemoryReportingSnapshotRepository(ReportingSnapshotRepository):
    """In-memory implementation of ReportingSnapshotRepository for unit testing."""

    def __init__(self):
        self._snapshots: Dict[str, ReportingSnapshot] = {}

    def save(self, snapshot: ReportingSnapshot) -> None:
        self._snapshots[snapshot.reporting_snapshot_id] = snapshot

    def get_by_id(self, snapshot_id: str) -> Optional[ReportingSnapshot]:
        return self._snapshots.get(snapshot_id)

    def get_all(self) -> List[ReportingSnapshot]:
        return list(self._snapshots.values())
