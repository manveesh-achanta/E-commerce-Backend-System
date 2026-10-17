from pydantic import BaseModel, ConfigDict
from models import OrderStatus
from datetime import datetime


class Create_Customer_model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name : str
    last_name : str
    email : str
    password : str
    phone_number : str
    address : str


class Customer_details_model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    first_name : str
    last_name : str
    email : str
    phone_number : str
    address : str


class Password_Change_model(BaseModel):
    old_password : str
    new_password : str


class OrderResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    seller_id: str
    customer_id: str
    product_id: str
    price: int
    order_date: datetime
    order_status: OrderStatus
    delivered_at: datetime | None