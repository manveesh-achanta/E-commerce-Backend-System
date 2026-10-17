from fastapi import APIRouter, Depends, HTTPException
from models import UserRole, Seller, Products, Orders, OrderStatus, Customer
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid7
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from starlette import status
from datetime import datetime, UTC


order_router = APIRouter(prefix="/order", tags=["Order"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]


@order_router.post("/place_order/{product_id}", status_code=status.HTTP_201_CREATED)
async def place_order(user : user_dependency, db : db_dependency, product_id : str):

    user_id = user.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    customer_query = select(Customer).where(Customer.user_id == user_id)
    customer_result = await db.execute(customer_query)
    customer = customer_result.scalar_one_or_none()

    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")

    query =  select(Products).where(Products.id == product_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Product Not Found")

    seller_id = result.seller_id
    price = result.price

    order_model = Orders(
        id = str(uuid7()),
        seller_id = seller_id,
        customer_id = customer.id,
        product_id = product_id,
        price = price,
        order_status = OrderStatus.PACKING,
        delivered_at = None
    )

    try:
        db.add(order_model)
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)
    return {"detail" : "Order Placed"}



@order_router.put("/change_status/{order_id}", status_code = status.HTTP_200_OK)
async def change_status(user_details : user_dependency, db : db_dependency, order_id : str, status_update : OrderStatus):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")
    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Orders).where(Orders.id == order_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Order Not Found")

    result.order_status = status_update

    if result.order_status == OrderStatus.DELIVERED:
        result.delivered_at = datetime.now(UTC)

    try:    
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)

    return {"detail" : "Status Changed"}




@order_router.get("/get_status/{order_id}", status_code = status.HTTP_200_OK)
async def get_status(user_details : user_dependency, db : db_dependency, order_id : str):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")
    
    query = select(Orders).where(Orders.id == order_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    order_status = result.order_status.value

    return {"Order Status" : order_status}




@order_router.put("/cancel_order/{order_id}", status_code = status.HTTP_200_OK)
async def cancel_order(user_details : user_dependency, db : db_dependency, order_id : str):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Orders).where(Orders.id == order_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Order Not Found")

    if result.customer is None or result.seller is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order has missing customer or seller associations")

    customer_id = result.customer.user_id
    seller_id = result.seller.user_id

    if user_id == customer_id:
        result.order_status = OrderStatus.CANCELLED
        try:    
            await db.flush()
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)
        return {"detail" : "Order Cancelled by Customer"}


    if user_id == seller_id:
        result.order_status = OrderStatus.CANCELLED
        try:    
            await db.flush()
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)
        return {"detail" : "Order Cancelled by Seller"}


    if user_role == UserRole.ADMIN:
        result.order_status = OrderStatus.CANCELLED
        try:    
            await db.flush()
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = exc)        
        return {"detail" : "Order Cancelled by Admin"}