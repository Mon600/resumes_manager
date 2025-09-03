import logging
from typing import Dict

from asyncpg import PostgresError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.db.repositories.user_repository import UserRepository
from src.schemas.AuthSchemas import RegisterUserSchema, LoginUserSchema
from src.security.auth import verify_password, hash_password
from src.security.jwt import create_token, decode_token





class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def get_tokens(self, user_id: int) -> Dict:
        data = {"user_id": user_id}
        access_token = await create_token(data)
        refresh_token = await create_token(data, token_type="refresh")

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def register(self, user_data: RegisterUserSchema) -> int:
        """
        Регистрация пользователя
        :param user_data: RegisterUserSchema
        :return: int
        """
        user_schema = user_data
        try:
            user_schema.password = await hash_password(user_schema.password)
            register_data = user_schema.model_dump(exclude={'password_repeat'})
            try:
                user_id = await self.repository.add(register_data)
                return user_id
            except IntegrityError as exc:
                self.logger.error(f"Ошибка добавления в БД {exc}")
                raise exc
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc


    async def login(self, login_data: LoginUserSchema):
        """
        Вход с помощью email и пароля
        :param login_data:
        :return:
        """
        try:
            user = await self.repository.get_by_email(login_data.email)
            if user is None:
                raise KeyError("Пользователь не найден")
            is_valid_password = await verify_password(user.password, login_data.password)
            if not is_valid_password:
                raise ValueError("Неверный пароль")

            return user
        except (PostgresError, SQLAlchemyError) as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc

    async def get_user_by_id(self, id: int):
        try:
            user = await self.repository.get_by_id(id)
            if user is None:
                raise KeyError("Пользователь не найден")
            return user
        except (PostgresError, SQLAlchemyError) as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc


    async def get_user(self, id: int):
        """
        Получения данных пользователя по его ID
        :param id:
        :return:
        """
        try:
            user = await self.repository.get_user(id)
            if user is None:
                raise KeyError("Пользователь не найден")
            return user
        except (PostgresError, SQLAlchemyError) as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc


    async def refresh(self, refresh_token: str) -> str | None:
        """
        Обновление access token'а
        :param refresh_token:
        :return:
        """

        token_data = await decode_token(refresh_token)

        if token_data.get("type") != "refresh":
            return None
        user_id = token_data["user_id"]
        access_token = await create_token({"user_id": user_id})
        return access_token