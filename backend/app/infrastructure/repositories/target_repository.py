from sqlalchemy.orm import Session

from app.domain.models.target import Target


class TargetRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, target: Target) -> Target:
        self.session.add(target)
        self.session.commit()
        self.session.refresh(target)
        return target

    def list_all(self) -> list[Target]:
        return self.session.query(Target).order_by(Target.id.desc()).all()

    def get_by_id(self, target_id: int) -> Target | None:
        return self.session.query(Target).filter(Target.id == target_id).first()
