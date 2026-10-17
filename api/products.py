from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import UserRole, Seller, Products
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid7
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from starlette import status
from schemas.product_schema import Create_Product_Model, Product_Modify_Model, List_Product_Response_Model


product_router = APIRouter(prefix="/products", tags=["Products"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]


@product_router.post("/add_products", status_code = status.HTTP_204_NO_CONTENT)
async def add_product(user_details : user_dependency, db : db_dependency, product_details : Create_Product_Model):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "User is Not a Seller")

    seller_id_query = select(Seller.id).where(Seller.user_id == user_id)
    result = await db.execute(seller_id_query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    product_model = Products(
        id = str(uuid7()),
        seller_id = query_result,
        product_name = product_details.product_name,
        product_description = product_details.product_description,
        price = product_details.price,
        stock = product_details.stock
    )
    try:
        db.add(product_model)
        await db.flush()
        await db.commit()
        await db.refresh(product_model)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc)

    return {"detail" : "Product Added"}




@product_router.put("/modify_products/{product_id}", status_code = status.HTTP_202_ACCEPTED)
async def modify_products(user_details : user_dependency, db : db_dependency, product_model : Product_Modify_Model, product_id : str):
    user_id = user_details.get("id")
    user_role = user_details.get("role")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")
    
    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "User is Not a Seller")

    query = select(Products).where(Products.id == product_id)
    result = await db.execute(query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if query_result.seller_details.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not the seller of this product")

    if product_model.product_name is not None:
        query_result.product_name = product_model.product_name

    if product_model.product_description is not None:
        query_result.product_description = product_model.product_description

    try:
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc)

    return {"detail" : "Product Modified"}




@product_router.get("/list_products", response_model=list[List_Product_Response_Model], status_code = status.HTTP_200_OK)
async def list_products(user_details : user_dependency, db : db_dependency, limit : int = 1000, skip : int = 0):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Products).order_by(Products.id).offset(skip).limit(limit)
    result = await db.execute(query)
    query_result = result.scalars().all()

    return query_result




@product_router.get("/list_products_by_seller/{seller_id}", status_code=status.HTTP_200_OK, response_model=list[List_Product_Response_Model])
async def get_products(db : db_dependency, seller_id : str, limit : int = Query(default = 10), skip : int = Query(default = 0)):
    
    if not seller_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid ID")

    query = select(Seller.id).where(Seller.id == seller_id)
    result = await db.execute(query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Seller Not Found")

    query = select(Products).where(Products.seller_id == seller_id).offset(skip).limit(limit)
    result = await db.execute(query)
    query_result = result.scalars().all()

    return  query_result




@product_router.put("/increase_stock/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def increase_stock(user_details : user_dependency, db : db_dependency, product_id : str, quantity : int = Query(gt=0)):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User ID")

    if not user_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User Data")

    query = select(Products).where(Products.id == product_id)
    result = await db.execute(query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Product Not Found")

    current_stock = query_result.stock
    query_result.stock = current_stock + quantity

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc)

    return {"detail" : "Quantity Increased"}




@product_router.put("/decrease_stock/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def decrease_stock(user_details : user_dependency, db : db_dependency, product_id : str, quantity : int = Query(gt=0)):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User ID")

    if not user_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User Data")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User Data")

    query = select(Products).where(Products.id == product_id)
    result = await db.execute(query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Product Not Found")

    current_stock = query_result.stock
    query_result.stock = current_stock - quantity

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc)

    return {"detail" : "Quantity Decreased"}




@product_router.put("/change_price/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def change_price(user_details : user_dependency, db : db_dependency, product_id : str, new_price : int = Query(ge = 0)):
    user_id = user_details.get("id")
    user_role = user_details.get("role")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User ID")
    
    if not user_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid User Data")
    
    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Only Seller can Modify")

    query = select(Products).where(Products.id == product_id)
    result = await db.execute(query)
    query_result = result.scalar_one_or_none()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Product Not Found")

    query_result.price = new_price
    
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc)

    return {"detail" : "Price Changed"}