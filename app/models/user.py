from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.core.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.COMPANY, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="user", uselist=False)


    def __repr__(self):
        return f"<User(id={self.id}, email=\'{self.login}\' , role=\'{self.role}\')>"