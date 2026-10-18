from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from models import UserRole, Users, Admin, Seller, Products
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid7
from sqlalchemy import select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from core.security import hash_password, verify_password_hash, create_token
from schemas.admin_schemas import Create_Admin_Model, Admin_Login_Model, Admin_Seller_Model, Admin_Products_Model
from starlette import status
from datetime import timedelta


admin_router = APIRouter(prefix="/admin", tags=["Admin"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]



@admin_router.post("/registration", status_code = status.HTTP_201_CREATED)
async def register_admin(user_details : user_dependency, db : db_dependency, admin_model : Create_Admin_Model):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Authorized for Admins")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    if result.role != user_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = 'You are not a Admin')

    password_hash = await run_in_threadpool(hash_password, admin_model.password)

    user_model = Users(
        id = str(uuid7()),
        email = admin_model.email,
        hashed_password  = password_hash,
        role = UserRole.ADMIN
    )

    new_admin = Admin(
        id = str(uuid7()),
        user_id = user_model.id,
        first_name = admin_model.first_name,
        last_name = admin_model.last_name,
        address = admin_model.address
    )

    try:
        db.add_all([user_model, new_admin])    
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email Already Registered")
    return {"detail" : "Admin Created"}




@admin_router.post("/admin_login", status_code=status.HTTP_201_CREATED)
async def login(db : db_dependency, login_details : Admin_Login_Model):

    email = login_details.email
    password = login_details.password

    query = select(Users).where(Users.email == email)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    password_hash = await run_in_threadpool(verify_password_hash, result.hashed_password, password)

    if not password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Incorrect Email or Password.")

    user_id = result.id
    username = result.email
    role = result.role

    token = create_token(username, role, user_id, timedelta(minutes=60))

    return {"access_token" : token, "token_type" : "bearer"}




@admin_router.get("/get_sellers", status_code=status.HTTP_200_OK, response_model=list[Admin_Seller_Model])
async def get_sellers(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Seller)
    execution = await db.execute(query)
    result = execution.scalars().all()

    return result



@admin_router.get("/get_seller/{seller_id}", status_code=status.HTTP_200_OK, response_model=Admin_Seller_Model)
async def get_seller_by_id(user_details : user_dependency, db : db_dependency, seller_id : str):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Seller).where(Seller.id == seller_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Seller Not Found")

    return result




@admin_router.get("/get_products", status_code=status.HTTP_200_OK, response_model=list[Admin_Products_Model])
async def get_products(user_details : user_dependency, db : db_dependency):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Products)
    execution = await db.execute(query)
    result = execution.scalars().all()

    return result




@admin_router.get("/get_products/{product_id}", status_code=status.HTTP_200_OK, response_model=Admin_Products_Model)
async def get_product(user_details : user_dependency, db : db_dependency, product_id : str):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Products).where(Products.id == product_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No Product Found")

    return result





@admin_router.get("/delete_user/{id}", status_code=status.HTTP_200_OK)
async def delete_user(user_details : user_dependency, db : db_dependency, id : str):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Users).where(Users.id == id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User Not Found")

    await db.delete(result)
    await db.commit()

    return {"detail" : "User Deleted"}





@admin_router.get("/delete_product/{id}", status_code=status.HTTP_200_OK)
async def delete_product(user_details : user_dependency, db : db_dependency, id : str):

    user_id = user_details.get("id")
    user_role = user_details.get("role")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    if user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Admin Not Found")

    result_user_role = result.role

    if result_user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid User")

    query = select(Products).where(Products.id == id)
    execution = await db.execute(query)
    result = execution.scalar_one_or_none()

    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User Not Found")

    await db.delete(result)
    await db.commit()

    return {"detail" : "Product Deleted"}