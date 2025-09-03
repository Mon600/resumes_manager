from typing import Annotated

from fastapi.params import Depends

from src.db.repositories.resume_repository import ResumeRepository
from src.db.repositories.user_repository import UserRepository
from src.api.DI.session_depends import session_dep


async def get_user_repository(session: session_dep) -> UserRepository:
    return UserRepository(session)


user_repository_dep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_resume_repository(session: session_dep) -> ResumeRepository:
    return ResumeRepository(session)


resume_repository_dep = Annotated[ResumeRepository, Depends(get_resume_repository)]


