from sqlalchemy.orm import Session

from app.domain.models.permission import Permission


class PermissionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)
        return permission

    def list_all(self) -> list[Permission]:
        return self.session.query(Permission).order_by(Permission.id.desc()).all()
