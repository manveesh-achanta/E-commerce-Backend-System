from pydantic import BaseModel, ConfigDict



class Create_Admin_Model(BaseModel):
    email : str
    password : str
    first_name : str
    last_name : str
    phone_number : str
    address : str



class Admin_Login_Model(BaseModel):
    email : str
    password : str



class Admin_Seller_Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    user_id : str
    first_name : str
    last_name : str
    phone_number : str
    address : str
    store_name : str



class Admin_Products_Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    seller_id : str
    product_name : str
    product_description : str
    price : int
    stock : int