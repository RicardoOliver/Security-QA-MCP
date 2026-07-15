from sqlalchemy.orm import Session

from app.domain.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()
