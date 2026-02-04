from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.auth_login import UserLoginRequest, UserLoginResponse
from schemas.auth_schemas import UserRegisterRequest, UserRegisterResponse
from services.auth_service import AuthService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Authorization"])
bearer_scheme = HTTPBearer()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: UserRegisterRequest, auth_service: AuthService = Depends()):
    user = await auth_service.register(request)
    return user


@router.post("/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest, auth_service: AuthService = Depends()):
    token = await auth_service.login(request)
    return token


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(),
):
    await auth_service.logout(access_token=credentials.credentials)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(),
):
    new_tokens = await auth_service.refresh_token(refresh_token=credentials.credentials)
    return new_tokens
