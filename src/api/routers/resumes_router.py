from asyncpg import PostgresError
from fastapi import APIRouter, HTTPException

from src.api.DI.service_depends import resume_service_dep
from src.api.DI.user_depends import user_id_dep
from src.schemas.PaginationSchemas import pagination_dep
from src.schemas.ResumeSchemas import ResumeSchema, GetResumeSchema, GetResumeContentSchema

router = APIRouter(prefix='/resume', tags=["Resume"])


@router.post('/new')
async def create_resume(resume_data: ResumeSchema, user_id: user_id_dep, service: resume_service_dep) -> GetResumeSchema:

    try:
        resume = await service.create_resume(resume_data, user_id)
        return resume
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.get('/user/{user_id}/resumes')
async def get_resumes_list(user_id: int, pagination: pagination_dep, service: resume_service_dep) -> list[GetResumeSchema]:
    try:
        resumes = await service.get_resumes(user_id, pagination)
        return resumes
    except KeyError:
        raise HTTPException(status_code=404, detail="Не найдено ни одного резюме")
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')



@router.get('/{resume_id}')
async def get_resume_by_id(resume_id: int, service: resume_service_dep) -> GetResumeSchema:
    try:
        resume = await service.get_resume(resume_id)
        return resume
    except KeyError:
        raise HTTPException(status_code=404, detail='Резюме не найдено')
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.put('/{resume_id}/edit')
async def edit_resume(
        resume_id: int,
        new_resume_data: ResumeSchema,
        user_id: user_id_dep,
        service: resume_service_dep) -> ResumeSchema:
    try:
        updated_resume = await service.edit_resume(resume_id, user_id, new_resume_data)
        return updated_resume
    except KeyError:
        raise HTTPException(status_code=404, detail='Резюме не найдено')
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.delete('/{resume_id}/delete')
async def delete_resume(resume_id: int, user_id: user_id_dep, service: resume_service_dep):
    try:
        resume_id = await service.delete_resume(resume_id, user_id)
        return {'ok': True, 'detail': f'Резюме {resume_id} успешно удалено'}
    except KeyError:
        raise HTTPException(status_code=404, detail='Резюме не найдено')
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')


@router.get('/{resume_id}/improve')
async def improve_resume(resume_id:int, service: resume_service_dep) -> GetResumeContentSchema:
    try:
        resume = await service.get_resume(resume_id)
        resume.content += ' [improved]'
        return resume
    except KeyError:
        raise HTTPException(status_code=404, detail='Резюме не найдено')
    except PostgresError:
        raise HTTPException(status_code=500, detail='Ошибка сервера')
