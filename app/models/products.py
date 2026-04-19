from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from app.core.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    is_discount = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    is_new = Column(Boolean, default=False, nullable=False)
    is_popular = Column(Boolean, default=False, nullable=False)
    is_chef_recommended = Column(Boolean, default=False, nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)
    old_price = Column(Numeric(10, 2), nullable=True)
    preparation_time = Column(Integer, nullable=True)
    status = Column(Boolean, default=True, nullable=False, index=True)

    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")

    __table_args__ = (
        Index("idx_products_company_title", "company_id", "title"),
        Index("idx_products_company_status_available", "company_id", "status", "is_available"),
    )


    def __repr__(self):
        return f"<Product(id={self.id}, title=\'{self.title}\')>"