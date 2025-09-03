import asyncio
import logging
import os
from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from src.api.DI.repository_depends import get_user_repository, get_resume_repository
from src.api.DI.service_depends import get_auth_service, get_resume_service
from src.api.DI.session_depends import get_session
from src.db.models.models import Base
from src.db.repositories.resume_repository import ResumeRepository
from src.db.repositories.user_repository import UserRepository
from src.security.jwt import create_token
from src.services.auth_service import AuthService
from src.services.resume_service import ResumeService


def get_test_db_url():
    return (
        f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/test_db"
    )


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_database():
    temp_url = "postgresql+asyncpg://postgres:1@localhost:5432/postgres"
    temp_engine = create_async_engine(temp_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

    async with temp_engine.begin() as conn:
        try:
            await conn.execute(text("DROP DATABASE IF EXISTS test_db WITH (FORCE)"))
        except Exception as e:
            print(f"Предупреждение: не удалось удалить базу: {e}")

        try:
            await conn.execute(text("CREATE DATABASE test_db"))
        except Exception as e:
            print(f"Ошибка: не удалось создать базу: {e}")
            raise

    await temp_engine.dispose()

    yield

    temp_engine = create_async_engine(temp_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with temp_engine.begin() as conn:
        try:
            await conn.execute(text("DROP DATABASE IF EXISTS test_heroes WITH (FORCE)"))
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
    await temp_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def engine(create_test_database):
    test_url = get_test_db_url()
    eng = create_async_engine(test_url, poolclass=NullPool)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield eng

    await eng.dispose()


@pytest_asyncio.fixture(scope="session")
async def sessionmaker(engine: engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def session(sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as conn:
        try:
            yield conn
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await conn.close()


@pytest_asyncio.fixture(scope="function")
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest_asyncio.fixture(scope="function")
async def resume_repository(session: AsyncSession) -> ResumeRepository:
    return ResumeRepository(session)



@pytest_asyncio.fixture(scope="function")
async def auth_service(
        user_repository: UserRepository,
) -> AuthService:
    service = AuthService(user_repository)
    service.logger = logging.getLogger("test")
    return service


@pytest_asyncio.fixture(scope="function")
async def resumes_service(
        resume_repository: ResumeRepository,
) -> ResumeService:
    service = ResumeService(resume_repository)
    service.logger = logging.getLogger("test")
    return service


@pytest_asyncio.fixture(scope="function", autouse=True)
async def configured_app() -> FastAPI:
    return app


@pytest_asyncio.fixture(scope="function")
def integration_override_dependencies(configured_app: FastAPI,
                                      session: AsyncSession,
                                      auth_service: AuthService,
                                      resumes_service: ResumeService,
                                      user_repository: UserRepository,
                                      resume_repository: ResumeRepository,

                                      ):
    configured_app.dependency_overrides[get_session] = lambda: session
    configured_app.dependency_overrides[get_user_repository] = lambda: user_repository
    configured_app.dependency_overrides[get_auth_service] = lambda: auth_service
    configured_app.dependency_overrides[get_resume_repository] = lambda: resume_repository
    configured_app.dependency_overrides[get_resume_service] = lambda: resumes_service

    yield
    configured_app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def async_client(configured_app: FastAPI, integration_override_dependencies) -> AsyncGenerator[AsyncClient, None]:
    BASE_URL = "http://test"
    async with AsyncClient(
            transport=ASGITransport(app=configured_app),
            base_url=BASE_URL
    ) as client:
        access_token = await create_token({'user_id': 1})
        refresh_token = await create_token({'user_id': 1}, token_type='refresh')
        client.cookies.set('access_token',
                           access_token)
        client.cookies.set('refresh_token',
                           refresh_token)
        yield client