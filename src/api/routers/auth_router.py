from asyncpg import PostgresError
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import Response

from src.api.DI.service_depends import auth_service_dep
from src.api.DI.user_depends import user_id_dep
from src.schemas.AuthSchemas import RegisterUserSchema, LoginUserSchema, GetUserSchema, GetUserExtendedSchema

router = APIRouter(prefix='/auth', tags=["Auth"])


@router.post('/register')
async def register(response:Response, data: RegisterUserSchema, service: auth_service_dep):
    try:
        user_id = await service.register(data)
        tokens = await service.get_tokens(user_id)

        response.set_cookie(
            "access_token",
            tokens["access_token"],
            max_age=1800,
            secure=True,
            httponly=True,
            samesite="none",
        )
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            max_age=43200 * 60,
            secure=True,
            httponly=True,
            samesite="none",
        )

        return {'ok': True, 'detail': 'Вы успешно зарегистрировались'}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже зарегистрирован")
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.post('/login')
async def login(response: Response, data: LoginUserSchema, service: auth_service_dep) -> GetUserSchema:
    try:
        user = await service.login(data)
        tokens = await service.get_tokens(user.id)
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            max_age=1800,
            secure=True,
            httponly=True,
            samesite="none",
        )
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            max_age=43200 * 60,
            secure=True,
            httponly=True,
            samesite="none",
        )

        return user
    except KeyError:
        raise HTTPException(status_code=404, detail="Пользователь с указанным email не найден")
    except ValueError:
        raise HTTPException(status_code=403, detail="Введен неверный пароль")
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.get('/user')
async def get_user_data(user_id: user_id_dep, service: auth_service_dep) -> GetUserExtendedSchema:
    try:
        user = await service.get_user(user_id)
        return user
    except KeyError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.post('/refresh')
async def refresh(request: Request, response: Response, service: auth_service_dep):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "Not  authorized")
    access_token = await service.refresh(refresh_token)
    response.set_cookie(
        "access_token",
        access_token,
        max_age=1800,
        secure=True,
        httponly=True,
        samesite="none",
    )
    return {'ok': True, 'access_token': access_token}


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return {'ok': True, 'detail': "Вы вышли из системы"}
