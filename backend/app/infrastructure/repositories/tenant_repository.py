from sqlalchemy.orm import Session

from app.domain.models.tenant import Tenant


class TenantRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def list_all(self) -> list[Tenant]:
        return self.session.query(Tenant).order_by(Tenant.id.desc()).all()
