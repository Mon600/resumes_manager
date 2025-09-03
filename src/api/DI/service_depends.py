from typing import Annotated

from fastapi.params import Depends

from src.api.DI.repository_depends import user_repository_dep, resume_repository_dep
from src.services.auth_service import AuthService
from src.services.resume_service import ResumeService


async def get_auth_service(repository: user_repository_dep) -> AuthService:
    return AuthService(repository)

auth_service_dep = Annotated[AuthService, Depends(get_auth_service)]


async def get_resume_service(repository: resume_repository_dep) -> ResumeService:
    return ResumeService(repository)


resume_service_dep = Annotated[ResumeService, Depends(get_resume_service)]