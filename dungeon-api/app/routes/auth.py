from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.schemas.user import Token, UserCreate
from app.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": "UNAUTHORIZED", "message": "Token invalide ou expiré."},
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register", status_code=201)
def register(user_in: UserCreate, session: Session = Depends(get_session)) -> dict[str, str]:
    existing = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "USER_EXISTS",
                "message": "Nom d'utilisateur déjà pris.",
            },
        )

    new_user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(new_user)
    session.commit()
    return {"message": "Compte créé avec succès."}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Identifiants incorrects.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {"sub": str(user.id), "username": user.username}
    )
    return Token(access_token=token, token_type="bearer")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise unauthorized()

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id.isdecimal():
        raise unauthorized()

    user = session.get(User, int(user_id))
    if user is None:
        raise unauthorized()
    return user
