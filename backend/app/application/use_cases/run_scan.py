import uuid
from datetime import datetime
from threading import Thread
import time

import sqlite3

from sqlalchemy import text

from app.core.database import engine
from app.core.observability import observer
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.scanners.factory import ScannerAdapterFactory


class InMemoryScanQueue:
    _instance: "InMemoryScanQueue | None" = None

    def __new__(cls) -> "InMemoryScanQueue":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.jobs: list[dict[str, object]] = []
        return cls._instance

    def enqueue(self, scan_id: int, execution_id: str) -> None:
        self.jobs.append({"scan_id": scan_id, "execution_id": execution_id})

    def dequeue(self) -> dict[str, object] | None:
        if not self.jobs:
            return None
        return self.jobs.pop(0)

    def size(self) -> int:
        return len(self.jobs)


class ScanWorker:
    def run(self, scan_id: int, execution_id: str) -> None:
        observer.record("scan_started", {"scan_id": scan_id, "execution_id": execution_id})
        connection = sqlite3.connect("security_qa.db")
        try:
            connection.execute(
                "UPDATE scans SET status = ?, updated_at = ? WHERE id = ?",
                ("running", datetime.utcnow(), scan_id),
            )
            connection.commit()
        finally:
            connection.close()

        scan_row = None
        connection = sqlite3.connect("security_qa.db")
        try:
            scan_row = connection.execute("SELECT target_url FROM scans WHERE id = ?", (scan_id,)).fetchone()
        finally:
            connection.close()

        target_url = scan_row[0] if scan_row else ""
        adapter = ScannerAdapterFactory.build()
        findings = adapter.run(target_url)
        if findings:
            session = None
            try:
                from app.core.database import SessionLocal
                from app.domain.models.finding import Finding

                session = SessionLocal()
                for finding in findings:
                    result = Finding(scan_id=scan_id, title=finding["title"], severity=finding.get("severity", "medium"), description=finding.get("description", ""))
                    session.add(result)
                session.commit()
            finally:
                if session is not None:
                    session.close()

        observer.record("scan_completed", {"scan_id": scan_id, "execution_id": execution_id})
        connection = sqlite3.connect("security_qa.db")
        try:
            connection.execute(
                "UPDATE scans SET status = ?, updated_at = ? WHERE id = ?",
                ("completed", datetime.utcnow(), scan_id),
            )
            connection.commit()
        finally:
            connection.close()


class RunScanUseCase:
    def __init__(self, repository: ScanRepository):
        self.repository = repository
        self.queue = InMemoryScanQueue()

    def execute(self, scan_id: int) -> dict[str, object]:
        scan = self.repository.get_by_id(scan_id)
        if not scan:
            raise ValueError("Scan not found")

        execution_id = str(uuid.uuid4())
        scan.status = "running"
        scan.updated_at = datetime.utcnow()
        self.repository.update(scan)
        self.queue.enqueue(scan.id, execution_id)
        worker = ScanWorker()
        thread = Thread(target=worker.run, args=(scan.id, execution_id), daemon=True)
        thread.start()
        thread.join(timeout=5)

        return {
            "scan_id": scan.id,
            "execution_id": execution_id,
            "status": "running",
            "queue_length": self.queue.size(),
            "observability": observer.snapshot(),
        }
