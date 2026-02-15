from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.auth_login import LogoutRequest, UserLoginRequest, UserLoginResponse
from schemas.auth_schemas import UserRegisterRequest, UserRegisterResponse
from schemas.reset_password import ForgotPasswordRequest, ResetPasswordRequest
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
    body: LogoutRequest = Body(default=LogoutRequest()),
    auth_service: AuthService = Depends(),
):
    await auth_service.logout(
        access_token=credentials.credentials,
        refresh_token=body.refresh_token,
    )
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(),
):
    new_tokens = await auth_service.refresh_token(refresh_token=credentials.credentials)
    return new_tokens


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest, auth_service: AuthService = Depends()
):
    await auth_service.forgot_password(request.email)
    return {"message": "OTP has been sent to your email"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest, auth_service: AuthService = Depends()
):
    await auth_service.reset_password(request)
    return {"message": "Password has been reset successfully"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    request: ResetPasswordRequest, auth_service: AuthService = Depends()
):
    await auth_service.verify_email(request)
    return {"message": "Email has been verified successfully"}


@router.get("/me", response_model=UserRegisterResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(),
):
    user_info = await auth_service.get_user_info(current_user["sub"])
    return user_info
