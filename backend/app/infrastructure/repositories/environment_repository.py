from sqlalchemy.orm import Session

from app.domain.models.environment import Environment


class EnvironmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, environment: Environment) -> Environment:
        self.session.add(environment)
        self.session.commit()
        self.session.refresh(environment)
        return environment

    def list_all(self) -> list[Environment]:
        return self.session.query(Environment).order_by(Environment.id.desc()).all()
