from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from database import Base
from enum import Enum
from sqlalchemy import Enum as sqlalchemyenum



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
    seller_details : Mapped[Seller | None] = relationship("Seller", back_populates="user_details", uselist=False, cascade="all, delete-orphan", lazy="selectin")



class Customer(Base):
    __tablename__ = "customer"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    user_id : Mapped[str] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable = False)
    first_name : Mapped[str] = mapped_column(String(100), nullable=False)
    last_name : Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number : Mapped[str | None] = mapped_column(String(20), nullable = True)
    address : Mapped[str | None] = mapped_column(String(400), nullable = True)
    user_details : Mapped[Users] = relationship("Users", back_populates = "customer_details", lazy = "selectin")



class Seller(Base):
    __tablename__ = "seller"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id : Mapped[str] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable=False)
    first_name : Mapped[str] = mapped_column(String(100), nullable = False)
    last_name : Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number : Mapped[str] = mapped_column(String(20), nullable = True)
    address : Mapped[str] = mapped_column(String(400), nullable = True)
    store_name : Mapped[str] = mapped_column(String(100), nullable = False, unique=True)
    user_details : Mapped[Users] = relationship("Users", back_populates="seller_details", lazy = "selectin")
    product_details : Mapped[list[Products] | None] = relationship("Products", back_populates="seller_details", lazy = "selectin")



class Products(Base):
    __tablename__ = "products"
    id : Mapped[str] = mapped_column(String(36), unique=True, nullable=False, primary_key=True)
    seller_id : Mapped[str] = mapped_column(ForeignKey(Seller.id, ondelete="CASCADE"), unique = False, nullable = False)
    product_name : Mapped[str] = mapped_column(String(36), nullable=False)
    product_description : Mapped[str] = mapped_column(String(300), nullable=True)
    price : Mapped[int] = mapped_column(Integer, nullable = False)
    stock : Mapped[int] = mapped_column(Integer, nullable=False)
    seller_details : Mapped[Seller] = relationship("Seller", back_populates="product_details", lazy = "selectin")