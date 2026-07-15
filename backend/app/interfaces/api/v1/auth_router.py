from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.use_cases.auth.authenticate_user import AuthenticateUserUseCase
from app.core.database import get_db
from app.core.observability import audit_trail
from app.core.security import decode_access_token
from app.infrastructure.repositories.user_repository import UserRepository
from app.interfaces.api.v1.schemas import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserResponse:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    repository = UserRepository(db)
    user = repository.get_by_username(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    repository = UserRepository(db)
    use_case = AuthenticateUserUseCase(repository)
    use_case.seed_default_user()
    try:
        result = use_case.execute(payload.username, payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    audit_trail.record(actor=payload.username, action="login", resource_type="auth", details={"username": payload.username})
    return TokenResponse(**result)


@router.get("/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
