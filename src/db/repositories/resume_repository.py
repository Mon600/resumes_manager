from sqlalchemy import select, Sequence, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.models import Resume
from src.schemas.ResumeSchemas import ResumeSchema


class ResumeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, resume_data: ResumeSchema, user_id: int) -> Resume:
        resume_dict = resume_data.model_dump()
        resume = Resume(**resume_dict, user_id = user_id)
        self.session.add(resume)
        await self.session.commit()
        return resume


    async def get_list(self, user_id: int, offset: int, limit: int) -> Sequence[Resume]:
        stmt = (
            select(Resume)
            .where(
                Resume.user_id == user_id,
                Resume.id > offset)
            .limit(limit))
        result = await self.session.execute(stmt)
        resumes = result.scalars().all()
        return resumes


    async def get_resume(self, resume_id: int) -> Resume:
        stmt = (
            select(Resume)
            .where(Resume.id == resume_id)
        )
        result = await self.session.execute(stmt)
        resumes = result.scalars().one_or_none()
        return resumes


    async def update(self, resume_id: int, user_id: int, new_data: ResumeSchema) -> Resume:
        new_data_dict = new_data.model_dump()
        stmt = (
            update(
                Resume
            )
            .where(
                Resume.id == resume_id,
                Resume.user_id == user_id
            )
            .values(
                **new_data_dict
            )
            .returning(
                Resume
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        updated_resume = result.scalars().first()
        return updated_resume


    async def delete_by_id(self, resume_id: int, user_id: int) -> int:
        stmt = (
            delete(Resume)
            .where(
                Resume.id == resume_id,
                Resume.user_id == user_id
            )
            .returning(Resume.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        deleted_resume_id = result.scalars().first()
        return deleted_resume_id