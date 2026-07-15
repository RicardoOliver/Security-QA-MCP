from sqlalchemy.orm import Session

from app.domain.models.permission import Permission
from app.domain.models.role import Role
from app.domain.models.role_permission import RolePermission


class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, role: Role) -> Role:
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def list_all(self) -> list[Role]:
        return self.session.query(Role).order_by(Role.id.desc()).all()

    def add_permission(self, role_id: int, permission_id: int) -> None:
        existing = (
            self.session.query(RolePermission)
            .filter(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id)
            .first()
        )
        if existing:
            return
        self.session.add(RolePermission(role_id=role_id, permission_id=permission_id))
        self.session.commit()

    def list_permissions(self, role_id: int) -> list[Permission]:
        return (
            self.session.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id == role_id)
            .all()
        )
