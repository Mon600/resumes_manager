from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field



class Pagination(BaseModel):
    cursor_offset: int = Field(default=0)
    limit: int = Field(default=10, description='Количество резюме в ответе')


pagination_dep = Annotated[Pagination, Query(...)]