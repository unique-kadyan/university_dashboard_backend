from datetime import date
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from entities.user import User
from repositories.user_repository import UserRepository
from schemas.auth_login import UserLoginRequest, UserLoginResponse
from schemas.auth_schemas import UserRegisterRequest
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token
from utils.token_blacklist import blacklist_token
from dtos.user_login_response import UserLoginResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository

    async def register(self, request: UserRegisterRequest) -> User:
        existing_email = await self.user_repository.find_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        existing_username = await self.user_repository.find_by_username(
            request.user_name
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        hashed_password = pwd_context.hash(request.password)

        user = User(
            user_type=request.user_type.value,
            email=request.email,
            user_name=request.user_name,
            hashed_password=hashed_password,
            first_name=request.first_name,
            middle_name=request.middle_name,
            last_name=request.last_name,
            date_of_birth=request.date_of_birth,
            gender=request.gender.value if request.gender else None,
            phone=request.phone,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            postal_code=request.postal_code,
            is_active=True,
            is_verified=False,
            created_at=date.today(),
        )

        return await self.user_repository.create(user)

    async def login(self, request: UserLoginRequest) -> UserLoginResponse:
        user = await self.user_repository.find_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not pwd_context.verify(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, access_token: str, refresh_token: str | None = None) -> None:
        await blacklist_token(access_token)
        if refresh_token:
            await blacklist_token(refresh_token)

    async def refresh_token(self, refresh_token: str) -> UserLoginResponse:
        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        user = await self.user_repository.find_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type,
        }
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return UserLoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
