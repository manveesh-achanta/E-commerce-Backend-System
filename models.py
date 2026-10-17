from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from database import Base
from enum import Enum
from sqlalchemy import Enum as sqlalchemyenum
from datetime import datetime



class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"



class OrderStatus(str, Enum):
    PACKING = "packing"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"



class ReturnStatus(str, Enum):
    RETURN_REQUESTED = "return_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PICKUP_SCHEDULED = "pickup_scheduled"
    RECEIVED = "received"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"




class Users(Base):
    __tablename__ = "users"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    email : Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    hashed_password : Mapped[str] = mapped_column(String(255), nullable = False)
    role : Mapped[UserRole] = mapped_column(sqlalchemyenum(UserRole, name = "user_role"), default = UserRole.CUSTOMER, nullable = False)
    customer_details : Mapped[Customer | None] = relationship("Customer", back_populates="user_details", uselist = False, cascade="all, delete-orphan", lazy = "selectin")
    seller_details : Mapped[Seller | None] = relationship("Seller", back_populates="user_details", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    admin_detail : Mapped[Admin | None] = relationship("Admin", back_populates="user_detail", lazy = "selectin")



class Customer(Base):
    __tablename__ = "customer"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    user_id : Mapped[str] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable = False)
    first_name : Mapped[str] = mapped_column(String(100), nullable=False)
    last_name : Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number : Mapped[str | None] = mapped_column(String(20), nullable = True)
    address : Mapped[str | None] = mapped_column(String(400), nullable = True)
    user_details : Mapped[Users] = relationship("Users", back_populates = "customer_details", lazy = "selectin")
    orders_list : Mapped[list[Orders]] = relationship("Orders", back_populates="customer", lazy = "selectin")
    return_details : Mapped[list[Returns]] = relationship("Returns", back_populates = "customer", lazy = "selectin")



class Seller(Base):
    __tablename__ = "seller"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id : Mapped[str] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable=False)
    first_name : Mapped[str] = mapped_column(String(100), nullable = False)
    last_name : Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number : Mapped[str] = mapped_column(String(20), nullable = False)
    address : Mapped[str] = mapped_column(String(400), nullable = False)
    store_name : Mapped[str] = mapped_column(String(100), nullable = False, unique=True)
    user_details : Mapped[Users] = relationship("Users", back_populates="seller_details", lazy = "selectin")
    product_details : Mapped[list[Products]] = relationship("Products", back_populates="seller_details", lazy = "selectin")
    order_details : Mapped[list[Orders]] = relationship("Orders", back_populates="seller", lazy = "selectin")



class Products(Base):
    __tablename__ = "products"
    id : Mapped[str] = mapped_column(String(36), unique=True, nullable=False, primary_key=True)
    seller_id : Mapped[str] = mapped_column(ForeignKey(Seller.id, ondelete="CASCADE"), unique = False, nullable = False)
    product_name : Mapped[str] = mapped_column(String(36), nullable=False)
    product_description : Mapped[str | None] = mapped_column(String(300), nullable=True)
    price : Mapped[int] = mapped_column(Integer, nullable = False)
    stock : Mapped[int] = mapped_column(Integer, nullable=False)
    seller_details : Mapped[Seller] = relationship("Seller", back_populates="product_details", lazy = "selectin")
    product_orders : Mapped[list[Orders]] = relationship("Orders", back_populates="product", lazy = "selectin")



class Orders(Base):
    __tablename__ = "orders"
    id : Mapped[str] = mapped_column(String(36), unique=True, nullable=False, primary_key=True)
    seller_id : Mapped[str] = mapped_column(ForeignKey(Seller.id, ondelete = "RESTRICT"), unique = False, nullable = False)
    customer_id : Mapped[str] = mapped_column(ForeignKey(Customer.id, ondelete = "RESTRICT"), unique = False, nullable = False)
    product_id : Mapped[str] = mapped_column(ForeignKey(Products.id, ondelete="RESTRICT"), unique=False, nullable = False)
    price : Mapped[int] = mapped_column(Integer, nullable=False)
    order_date : Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable = False)
    order_status : Mapped[OrderStatus] = mapped_column(sqlalchemyenum(OrderStatus, name = "Order_Status"), nullable = False)
    delivered_at : Mapped[datetime | None] = mapped_column(DateTime(), nullable = True)
    customer : Mapped[Customer] = relationship("Customer", back_populates="orders_list", lazy = "selectin")
    seller : Mapped[Seller] = relationship("Seller", back_populates="order_details", lazy = "selectin")
    product : Mapped[Products] = relationship("Products", back_populates="product_orders", lazy = "selectin")
    returns : Mapped[Returns] = relationship("Returns", back_populates="return_orders", lazy = "selectin")



class Returns(Base):
    __tablename__ = "returns"
    id : Mapped[str] = mapped_column(String(36), unique=True, nullable = False, primary_key = True)
    customer_id : Mapped[str] = mapped_column(ForeignKey(Customer.id, ondelete = "RESTRICT"), unique = False, nullable = False)
    order_id : Mapped[str] = mapped_column(ForeignKey(Orders.id, ondelete = "RESTRICT"), unique = False, nullable = False)
    reason : Mapped[str | None] = mapped_column(String(300), nullable=True)
    requested_at : Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable=False) #timezone = True
    return_status : Mapped[ReturnStatus] = mapped_column(sqlalchemyenum(ReturnStatus, name = "Return_Status"), nullable = False)
    return_orders : Mapped[Orders] = relationship("Orders", back_populates="returns", lazy = "selectin")
    customer : Mapped[Customer] = relationship("Customer", back_populates="return_details", lazy = "selectin")



class Admin(Base):
    __tablename__ = "Admin"
    id : Mapped[str] = mapped_column(String(36), primary_key=True, index = True)
    user_id : Mapped[str] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"), unique = True, nullable = False)
    first_name : Mapped[str] = mapped_column(String(100), nullable=False)
    last_name : Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number : Mapped[str | None] = mapped_column(String(20), nullable = True)
    address : Mapped[str | None] = mapped_column(String(400), nullable = True)
    user_detail : Mapped[Users] = relationship("Users", back_populates="admin_detail", lazy = "selectin")