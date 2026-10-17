from fastapi import APIRouter, Depends, HTTPException
from models import UserRole, Customer, Returns, ReturnStatus
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid7
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from starlette import status
from datetime import datetime, UTC
from schemas.return_schemas import Return_Model, ReturnResponseModel


return_router = APIRouter(prefix="/return", tags=["Returns"])

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]



@return_router.post("/return_order/{order_id}", status_code=status.HTTP_201_CREATED)
async def return_order(user_details : user_dependency, db : db_dependency, order_id : str, reason : Return_Model):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    query = select(Customer).where(Customer.user_id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    return_model = Returns(
        id = str(uuid7()),
        customer_id = result.id,
        order_id = order_id,
        reason = reason.reason_for_return,
        requested_at = datetime.now(UTC),
        return_status = ReturnStatus.RETURN_REQUESTED
    )

    try:
        db.add(return_model)
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Unable to Create the return request")

    return {"detail" : "Return Sucessfull"}




@return_router.put("/change_return_status/{return_id}", status_code = status.HTTP_202_ACCEPTED)
async def change_return_status(user_details : user_dependency, db : db_dependency, new_return_status : ReturnStatus, return_id : str):

    user_role = user_details.get("role")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not allowed to change the status")

    query = select(Returns).where(Returns.id == return_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail = "No Returns Found")

    result.return_status = new_return_status

    try:
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)

    return {"detail" : "Status Update Done"}




@return_router.get("/get_returns", response_model=list[ReturnResponseModel], status_code = status.HTTP_200_OK)
async def returns_of_customers(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid Token")

    query = select(Customer).where(Customer.user_id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer Not Found")

    returns_result = result.return_details

    return returns_result