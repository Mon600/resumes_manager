from pydantic import BaseModel, Field


class ResumeSchema(BaseModel):
    title: str = Field(max_length=64, description="Название резюме")
    content: str = Field(max_length=1024, description="Контент резюме")


class GetResumeSchema(ResumeSchema):
    id: int

class GetResumeContentSchema(BaseModel):
    content: str = Field(max_length=1024, description="Контент резюме")
