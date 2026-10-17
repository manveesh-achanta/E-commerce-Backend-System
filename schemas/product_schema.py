from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Optional



class Create_Product_Model(BaseModel):
    product_name : str
    product_description : str
    price : int
    stock : int



class Product_Modify_Model(BaseModel):
    product_name : Annotated[Optional[str], Field(default=None)]
    product_description : Annotated[Optional[str], Field(default=None)]


class List_Product_Response_Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    seller_id : str
    product_name : str
    product_description : str | None
    price : int 
    stock : int