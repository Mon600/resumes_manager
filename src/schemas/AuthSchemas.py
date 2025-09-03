from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator



class GetUserSchema(BaseModel):
    first_name: Optional[str] = Field(default="Пользователь", description="Имя", max_length=64)
    last_name: Optional[str] = Field(default='', description="Фамилия", max_length=64)
    email: EmailStr = Field(description="Email пользователя")
    resumes_count: int = Field(description="Счетчик резюме пользователя")


class GetUserExtendedSchema(GetUserSchema):
    id: int = Field(description='ID')

class LoginUserSchema(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(default='', description="Пароль", min_length=8)


class RegisterUserSchema(LoginUserSchema):
    first_name: Optional[str] = Field(default="Пользователь", description="Имя", max_length=64)
    last_name: Optional[str] = Field(default=None, description="Фамилия", max_length=64)
    password_repeat: str = Field(default='', description="Повтор пароля", min_length=8)

    @model_validator(mode="before")
    def validate(cls, value: Dict[str, str]) -> Dict[str, str]:
        password = value.get('password', None)
        password_repeat = value.get('password_repeat', None)
        if password != password_repeat:
            raise ValueError("Passwords doesn't match. Check it again.")
        return value


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(min_length=8, description="Старый пароль")
    new_password: str = Field(min_length=8, description="Новый пароль")
    new_password_repeat: str = Field(min_length=8, description="Подтверждение пароля")

    @model_validator(mode="before")
    def validate(cls, value: Dict[str, str]) -> Dict[str, str]:
        new_password = value.get('new_password', None)
        new_password_repeat = value.get('new_password_repeat', None)
        if new_password != new_password_repeat:
            raise ValueError("New password and confirm doesn't match")
        return value


