
from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
    BackgroundTasks
)
 
from .schemas import (
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)
 
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
 
from .utils import (
    create_access_token,
    generate_passwd_hash,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token
)
 
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
 
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker
)
 
from src.db.redis import add_jti_to_blocklist
 
from src.errors import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken
)
 
from src.config import Config
from src.mail import mail, create_message, send_email_direct
 
# Rate limiter
from src.rate_limit import limiter
 
 
auth_router = APIRouter()
 
user_service = UserService()
 
admin_role_checker = RoleChecker(["admin"])
user_role_checker = RoleChecker(["user", "admin"])
 
REFRESH_TOKEN_EXPIRY = 2
 
 
# ---------------------------------------------------------
# SEND MAIL
# ---------------------------------------------------------
 
@auth_router.post(
    "/send_mail",
    responses={
        400: {"description": "Invalid request body"}
    }
)
@limiter.limit("5/minute")
async def send_mail(
    request: Request,
    emails: EmailModel,
    background_tasks: BackgroundTasks
):
 
    emails = emails.addresses
 
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to the app"
 
    background_tasks.add_task(
        send_email_direct,
        emails,
        subject,
        html
    )
 
    return {
        "message": "Email sent successfully"
    }
 
 
# ---------------------------------------------------------
# SIGNUP
# ---------------------------------------------------------
 
@auth_router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {
            "description": "User with email already exists"
        }
    }
)
@limiter.limit("3/minute")
async def create_user_Account(
    request: Request,
    user_data: UserCreateModel,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
 
    """
    Create user account using email, username,
    first_name, last_name
    """
 
    email = user_data.email
 
    user_exists = await user_service.user_exists(
        email,
        session
    )
 
    if user_exists:
        raise UserAlreadyExists()
 
    new_user = await user_service.create_user(
        user_data,
        session
    )
 
    token = create_url_safe_token({
        "email": email
    })
 
    link = (
        f"http://{Config.DOMAIN}"
        f"/api/v1/auth/verify/{token}"
    )
 
    html_message = f"""
    <h1>Verify Email</h1>
 
    <p>
        Please Click this
        <a href="{link}">link</a>
        to verify your email
    </p>
    """
 
    emails = [email]
 
    subject = "Verify Your email"
 
    background_tasks.add_task(
        send_email_direct,
        emails,
        subject,
        html_message
    )
 
    return {
        "message": (
            "Account Created! "
            "Check email to verify your account"
        ),
        "user": new_user
    }
 
 
# ---------------------------------------------------------
# VERIFY ACCOUNT
# ---------------------------------------------------------
 
@auth_router.get(
    "/verify/{token}",
    responses={
        400: {
            "description": "Invalid or expired token"
        }
    }
)
@limiter.limit("10/minute")
async def verify_user_account(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session)
):
 
    token_data = decode_url_safe_token(token)
 
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
 
    user_email = token_data.get("email")
 
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
 
    user = await user_service.get_user_by_email(
        user_email,
        session
    )
 
    if not user:
        raise UserNotFound()
 
    await user_service.update_user(
        user,
        {"is_verified": True},
        session
    )
 
    return JSONResponse(
        content={
            "message": "Account verified successfully"
        },
        status_code=status.HTTP_200_OK
    )
 
 
# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
 
@auth_router.post(
    "/login",
    responses={
        400: {
            "description": "Invalid email or password"
        }
    }
)
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session)
):
 
    email = login_data.email
    password = login_data.password
 
    user = await user_service.get_user(
        email,
        session
    )
 
    if user is not None:
 
        password_valid = verify_password(
            password,
            user.password_hash
        )
 
        if password_valid:
 
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_id": str(user.uid),
                    "role": user.role
                }
            )
 
            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_id": str(user.uid)
                },
                refresh=True,
                expiry=timedelta(
                    days=REFRESH_TOKEN_EXPIRY
                )
            )
 
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
 
    raise InvalidCredentials()
 
 
# ---------------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------------
 
@auth_router.get(
    "/refresh_token",
    responses={
        401: {
            "description": "Not authenticated"
        }
    }
)
async def get_new_access_token(
    token_details: dict = Depends(
        RefreshTokenBearer()
    )
):
 
    expiry_timestamp = token_details["exp"]
 
    if datetime.fromtimestamp(
        expiry_timestamp
    ) > datetime.now():
 
        new_access_token = create_access_token(
            user_data=token_details["user"]
        )
 
        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
 
    raise InvalidToken()
 
 
# ---------------------------------------------------------
# CURRENT USER
# ---------------------------------------------------------
 
@auth_router.get(
    "/me",
    response_model=UserBooksModel,
    responses={
        401: {
            "description": "Not authenticated"
        }
    }
)
async def get_current_user(
    user=Depends(get_current_user)
):
 
    return user
 
 
# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
 
@auth_router.delete(
    "/users/{user_id}",
    dependencies=[
        Depends(admin_role_checker)
    ],
    responses={
        401: {
            "description": "Not authenticated"
        }
    }
)
async def delete_user(
    user_id: str
):
 
    return {
        "message": "User deleted successfully"
    }
 
 
# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
 
@auth_router.get(
    "/logout",
    responses={
        401: {
            "description": "Not authenticated"
        }
    }
)
async def revoke_token(
    token_details: dict = Depends(
        AccessTokenBearer()
    )
):
 
    jti = token_details["jti"]
 
    await add_jti_to_blocklist(jti)
 
    return JSONResponse(
        content={
            "message": "Logout Our Successfully"
        },
        status_code=status.HTTP_200_OK
    )
 
 
# ---------------------------------------------------------
# PASSWORD RESET REQUEST
# ---------------------------------------------------------
 
@auth_router.post(
    "/password-reset-request",
    responses={
        400: {
            "description": "Invalid request body"
        }
    }
)
@limiter.limit("3/minute")
async def password_reset_request(
    request: Request,
    email_data: PasswordResetRequestModel,
    background_tasks: BackgroundTasks
):
 
    email = email_data.email
 
    token = create_url_safe_token({
        "email": email
    })
 
    link = (
        f"http://{Config.DOMAIN}"
        f"/api/v1/auth/password-reset-confirm/{token}"
    )
 
    html_message = f"""
    <h1>Reset Your Password</h1>
 
    <p>
        Please Click this
        <a href="{link}">link</a>
        to reset your password
    </p>
    """
 
    subject = "Reset Your Password"
 
    background_tasks.add_task(
        send_email_direct,
        [email],
        subject,
        html_message
    )
 
    return JSONResponse(
        content={
            "message": (
                "Please check your email for "
                "instructions to reset your password"
            )
        },
        status_code=status.HTTP_200_OK
    )
 
 
# ---------------------------------------------------------
# PASSWORD RESET CONFIRM
# ---------------------------------------------------------
 
@auth_router.post(
    "/password-reset-confirm/{token}",
    responses={
        400: {
            "description": (
                "Invalid or expired token / "
                "passwords do not match"
            )
        }
    }
)
@limiter.limit("5/minute")
async def reset_account_password(
    request: Request,
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session)
):
 
    token_data = decode_url_safe_token(token)
 
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
 
    user_email = token_data.get("email")
 
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
 
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
 
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
 
    user = await user_service.get_user(
        user_email,
        session
    )
 
    if not user:
        raise UserNotFound()
 
    passwd_hash = generate_passwd_hash(
        new_password
    )
 
    await user_service.update_user(
        user,
        {
            "password_hash": passwd_hash
        },
        session
    )
 
    return JSONResponse(
        content={
            "message": "Password reset Successfully"
        },
        status_code=status.HTTP_200_OK
    )
 
