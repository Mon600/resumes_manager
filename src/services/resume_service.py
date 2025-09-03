import logging

from asyncpg import PostgresError
from sqlalchemy import Sequence

from src.db.models.models import Resume
from src.db.repositories.resume_repository import ResumeRepository
from src.schemas.PaginationSchemas import Pagination
from src.schemas.ResumeSchemas import ResumeSchema


class ResumeService:
    def __init__(self, repository: ResumeRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def create_resume(self, resume_data: ResumeSchema, user_id: int) -> Resume:
        try:
            resume = await self.repository.add(resume_data, user_id)
            return resume
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc

    async def get_resumes(self, user_id: int, pagintion: Pagination) -> Sequence[Resume]:
        try:
            resumes = await self.repository.get_list(user_id, pagintion.cursor_offset, pagintion.limit)
            if not resumes:
                raise KeyError("Не найдено ни одного резюме")
            return resumes
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc


    async def get_resume(self, resume_id: int) -> Resume:
        try:
            resume = await self.repository.get_resume(resume_id)
            if not resume:
                raise KeyError("Резюме не найдено")
            return resume
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc

    async def edit_resume(self, resume_id: int, user_id: int, new_data: ResumeSchema) -> Resume:
        try:
            updated_resume = await self.repository.update(resume_id, user_id, new_data)
            if not updated_resume:
                raise KeyError("Резюме не найдено.")
            return updated_resume
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc

    async def delete_resume(self, resume_id: int, user_id: int) -> int:
        try:
            deleted_resume_id = await self.repository.delete_by_id(resume_id, user_id)
            if not deleted_resume_id:
                raise KeyError("Резюме не найдено.")
            return deleted_resume_id
        except PostgresError as exc:
            self.logger.error(f"Ошибка взаимодействия с базой данных {exc}")
            raise exc
