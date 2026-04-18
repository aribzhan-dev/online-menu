from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.core.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    wifi_password = Column(String, nullable=True)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    status = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="company")
    categories = relationship("Category", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"