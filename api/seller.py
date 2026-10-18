from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from models import Users, UserRole, Seller
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from core.security import create_token, hash_password, verify_password_hash
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid7
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from schemas.seller_schema import Create_seller_model, Seller_Details_Model, Change_Password_Model, OrderResponse, Product_Response_Model


seller_router = APIRouter(prefix="/seller", tags=["Seller"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]



@seller_router.post("/create_seller", status_code=status.HTTP_201_CREATED)
async def create_seller(seller_details : Create_seller_model, db : db_dependency):
    password_hash = await run_in_threadpool(hash_password, seller_details.password)

    user_model = Users(
        id = str(uuid7()),
        email = seller_details.email.lower(),
        hashed_password = password_hash,
        role = UserRole.SELLER
    )

    seller_model = Seller(
        id = str(uuid7()),
        first_name = seller_details.first_name,
        last_name = seller_details.last_name,
        phone_number = seller_details.phone_number,
        address = seller_details.address,
        store_name = seller_details.store_name.lower(),
        user_details = user_model
    )

    query = select(Seller).where(Seller.store_name == seller_details.store_name.lower())
    result = await db.execute(query)
    store_result = result.scalar_one_or_none()
    
    if store_result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Store Name Already Registered")

    try:
        db.add_all([user_model, seller_model])
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email Already Registered")
    return {"details" : "Seller Created"}




@seller_router.post("/seller_login", status_code=status.HTTP_200_OK)
async def seller_login(db : db_dependency, login_model : Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = login_model.username
    password = login_model.password

    query = select(Users).where(Users.email == email)
    execute = await db.execute(query)
    result = execute.scalar_one_or_none()

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    if result.role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not a seller.")

    verification = await run_in_threadpool(verify_password_hash, result.hashed_password, password)

    if not verification:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Username or Password")

    token = create_token(result.email, result.role, result.id, timedelta(minutes=20))

    return {"access_token" : token, "token_type" : "bearer"}




@seller_router.get("/details", status_code=status.HTTP_200_OK)
async def get_details(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")
    role = user_details.get("role")

    if role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not a seller.")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    query = select(Seller).where(Seller.user_id == user_id)

    result = await db.execute(query)

    seller_details = result.scalar_one_or_none()

    if seller_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer Not Found")

    details = Seller_Details_Model.model_validate({
        "id" : seller_details.id,
        "first_name" : seller_details.first_name,
        "last_name" : seller_details.last_name,
        "address" : seller_details.address,
        "phone_number" : seller_details.phone_number,
        "email" : seller_details.user_details.email,
        "store_name" : seller_details.store_name
    })

    return details




@seller_router.get("/get_products", status_code=status.HTTP_200_OK, response_model=list[Product_Response_Model])
async def get_products(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not a seller.")

    query = select(Seller).where(Seller.user_id == user_id)
    execute = await db.execute(query)
    seller_details = execute.scalar_one_or_none()

    if seller_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Seller Not Found")

    products = seller_details.product_details

    if not products:
        return []

    products_list = []

    for product in products:
        product_model = Product_Response_Model.model_validate(product)
        products_list.append(product_model)

    return products_list




@seller_router.put("/change_password", status_code = status.HTTP_202_ACCEPTED)
async def change_password(password_model : Change_Password_Model, user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not a seller.")

    query = select(Users).where(Users.id == user_id)
    
    result = await db.execute(query)
    
    query_result = result.scalar_one_or_none()
    
    if query_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Seller Not Found")

    verification = await run_in_threadpool(verify_password_hash, query_result.hashed_password, password_model.old_password)

    if not verification:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Password does nor match")

    query_result.hashed_password = await run_in_threadpool(hash_password, password_model.new_password)

    try:
        await db.flush()
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Failed to update Password")
    
    return {"detail" : "Password Changed Successfuly"}




@seller_router.get("/get_orders", response_model = list[OrderResponse], status_code = status.HTTP_200_OK)
async def get_orders(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    if user_role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not a seller.")

    query = select(Seller).where(Seller.user_id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    if not result.order_details:
        return []

    orders = []
    
    for order in result.order_details:
        order_model = OrderResponse.model_validate(order)
        orders.append(order_model)

    return orders