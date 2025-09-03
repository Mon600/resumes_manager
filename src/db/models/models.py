from typing import List, Annotated

from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[pk]
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), default="Пользователь")
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    resumes_rel: Mapped[List["Resume"]] = relationship(back_populates='user_rel')


class Resume(Base):
    __tablename__ = 'resumes'

    id: Mapped[pk]
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(String(1024), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    user_rel: Mapped["User"] = relationship(back_populates='resumes_rel')
