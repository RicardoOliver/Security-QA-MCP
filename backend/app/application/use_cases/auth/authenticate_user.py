from app.core.security import create_access_token, hash_password, verify_password
from app.domain.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository


class AuthenticateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, password: str) -> dict[str, str]:
        user = self.repository.get_by_username(username)
        if not user:
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise PermissionError("Inactive user")
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        token = create_access_token(user.username)
        return {"access_token": token, "token_type": "bearer"}

    def seed_default_user(self) -> None:
        existing = self.repository.get_by_username("admin")
        if not existing:
            self.repository.create(
                User(username="admin", password_hash=hash_password("password123"), is_active=True)
            )
