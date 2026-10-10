from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, UUID
from database import Base
from enum import Enum
from sqlalchemy import Enum as sqlalchemyenum
from uuid import uuid7, UUID as PyUUID


class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"


class Users(Base):
    __tablename__ = "users"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    email : Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    hashed_password : Mapped[str] = mapped_column(String(255), nullable = False)
    role : Mapped[UserRole] = mapped_column(sqlalchemyenum(UserRole, name = "user_role"), default = UserRole.CUSTOMER, nullable = False)
    customer_details : Mapped[Customer | None] = relationship("Customer", back_populates="user_details", uselist = False, cascade="all, delete-orphan", lazy = "selectin")


class Customer(Base):
    __tablename__ = "customer"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    user_id : Mapped[int] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable = False)
    first_name : Mapped[str] = mapped_column(String(100), nullable=False)
    last_name : Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number : Mapped[str | None] = mapped_column(String(20), nullable = True)
    address : Mapped[str | None] = mapped_column(String(400), nullable = True)
    user_details : Mapped[Users] = relationship("Users", back_populates = "customer_details", lazy = "selectin")