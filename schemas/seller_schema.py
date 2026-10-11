from pydantic import BaseModel, ConfigDict

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