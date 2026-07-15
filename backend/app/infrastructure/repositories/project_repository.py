from sqlalchemy.orm import Session

from app.domain.models.project import Project


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def list_all(self) -> list[Project]:
        return self.session.query(Project).order_by(Project.id.desc()).all()
