from pydantic import BaseModel, ConfigDict
from typing import Annotated


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
    first_name : str
    last_name : str
    email : str
    phone_number : str
    address : str


class Password_Change_model(BaseModel):
    old_password : str
    new_password : str