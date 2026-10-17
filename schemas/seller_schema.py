from pydantic import BaseModel, ConfigDict, AliasPath, Field
from models import OrderStatus
from datetime import datetime



class Create_seller_model(BaseModel):
    email : str
    password : str
    first_name : str
    last_name : str
    phone_number : str
    address : str
    store_name : str



class Seller_Details_Model(BaseModel):
    id : str
    email : str
    first_name : str
    last_name : str
    phone_number : str
    address : str
    store_name : str



class Change_Password_Model(BaseModel):
    old_password : str
    new_password : str



class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    product_name : str = Field(validation_alias=AliasPath("product", "product_name"))
    price : int
    order_status : OrderStatus
    order_date : datetime
    delivered_at : str | None



class Product_Response_Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    product_name : str
    product_description : str
    price : int
    stock : int