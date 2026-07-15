from sqlalchemy.orm import Session

from app.domain.models.scan import Scan


class ScanRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, scan: Scan) -> Scan:
        self.session.add(scan)
        self.session.commit()
        self.session.refresh(scan)
        return scan

    def list_all(self) -> list[Scan]:
        return self.session.query(Scan).order_by(Scan.id.desc()).all()

    def get_by_id(self, scan_id: int) -> Scan | None:
        return self.session.query(Scan).filter(Scan.id == scan_id).first()

    def update(self, scan: Scan) -> Scan:
        self.session.add(scan)
        self.session.commit()
        self.session.refresh(scan)
        return scan
