
from typing import Any, Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from starlette.requests import Request

from src.api.DI.service_depends import auth_service_dep
from src.security.jwt import decode_token

#
# async def get_current_user(request: Request, service: auth_service_dep):
#     access_token = request.cookies.get('access_token')
#     if not access_token:
#         raise HTTPException(401, "Not authorized")
#     payload = await decode_token(access_token)
#     user_id = payload.get('user_id')
#     try:
#         user = service.get_user(user_id)
#         return user
#     except KeyError:
#         raise HTTPException(403, "No access")
#
#
# user_dep = Annotated[Any, Depends(get_current_user)]


async def get_current_user_id(request: Request):
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise HTTPException(401, "Not authorized")
    payload = await decode_token(access_token)
    user_id = payload.get('user_id')
    return user_id


user_id_dep = Annotated[int, Depends(get_current_user_id)]