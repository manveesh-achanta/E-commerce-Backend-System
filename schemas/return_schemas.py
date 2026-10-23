from pydantic import BaseModel, ConfigDict
from models import ReturnStatus
from datetime import datetime


class Return_Model(BaseModel):
    reason_for_return : str


class ReturnResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    customer_id : str
    order_id : str
    requested_at : datetime
    return_status : ReturnStatus