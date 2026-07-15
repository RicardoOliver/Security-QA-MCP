from sqlalchemy.orm import Session

from app.domain.models.finding import Finding


class FindingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, finding: Finding) -> Finding:
        self.session.add(finding)
        self.session.commit()
        self.session.refresh(finding)
        return finding

    def list_all(self) -> list[Finding]:
        return self.session.query(Finding).all()

    def list_by_scan_id(self, scan_id: int) -> list[Finding]:
        return self.session.query(Finding).filter(Finding.scan_id == scan_id).all()
