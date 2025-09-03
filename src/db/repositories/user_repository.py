from typing import Dict

from pydantic import EmailStr
from sqlalchemy import update, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.models import User, Resume
from src.schemas.AuthSchemas import RegisterUserSchema, GetUserSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_data: Dict[str, str]) -> int:
        """
        Добавление пользователя в БД
        :param user_data: RegisterUserSchema
        :return: int
        """
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        return new_user.id


    async def get_by_email(self, email: EmailStr):
        """
        Получение пользователя по email
        :param email:
        :return:
        """

        resume_count_subquery = (
            select(
                func.count(Resume.id)
            )
            .where(Resume.user_id == User.id)
            .scalar_subquery()
            .label("resumes_count")
        )

        stmt = (
            select(
                User,
                resume_count_subquery
            )
            .where(User.email == email)
        )

        result = await self.session.execute(stmt)
        row = result.one_or_none()

        if not row:
            return None

        user = row[0]
        user.resumes_count = row[1]

        return user


    async def get_by_id(self, id: int):
        stmt = select(User).where(User.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()


    async def get_user(self, id: int):
        """
        Получение данных пользователя и количество его резюме
        :param id:
        :return:
        """
        resume_count_subquery = (
            select(
                func.count(Resume.id)
            )
            .where(Resume.user_id == User.id)
            .scalar_subquery()
            .label("resumes_count")
        )

        stmt = (
            select(
                User,
                resume_count_subquery
            )
            .where(User.id == id)
        )

        result = await self.session.execute(stmt)
        row = result.one_or_none()

        if not row:
            return None

        user = row[0]
        user.resumes_count = row[1]

        return user



    async def change_password_by_id(self, id: int, hash_password: str):
        """
        Меняем хеш пароля пользователя по его ID
        :param id:
        :param hash_password:
        :return: bool
        """
        stmt = (update(User)
                .where(User.id == id)
                .values(password=hash_password))
        await self.session.execute(stmt)
        await self.session.commit()
        return True