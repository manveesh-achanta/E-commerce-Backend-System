from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from models import Users, Customer, UserRole
from dependencies.database_dependency import get_db
from dependencies.token_dependency import token_bearer
from core.security import create_token, hash_password, verify_password_hash
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.customer_schema import Create_Customer_model, Customer_details_model, Password_Change_model
from uuid import uuid7
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

customer_router = APIRouter(prefix="/customer", tags=["Customer"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict[str, any], Depends(token_bearer)]



@customer_router.post("/create_customer", status_code=status.HTTP_201_CREATED)
async def create_customer(customer_details : Create_Customer_model, db : db_dependency):

    password = await run_in_threadpool(hash_password, customer_details.password)
    
    customer_model = Customer(
        id = str(uuid7()),
        first_name = customer_details.first_name,
        last_name = customer_details.last_name,
        phone_number = customer_details.phone_number,
        address = customer_details.address
    )

    user_model = Users(
        id = str(uuid7()),
        email = customer_details.email.lower(),
        hashed_password = password,
        role = UserRole.CUSTOMER,
        customer_details = customer_model
    )

    try:
        db.add_all([user_model, customer_model])        
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email Already Registered")



@customer_router.post("/customer_login")
async def customer_login(login_model : Annotated[OAuth2PasswordRequestForm, Depends()], db : db_dependency):
    email = login_model.username.lower()
    query = select(Users).where(Users.email == email)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User Not Found")

    password_result = await run_in_threadpool(verify_password_hash, existing.hashed_password, login_model.password)

    if not password_result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Email or Password Incorrect.")

    email = existing.email
    role = existing.role.value
    user_id = existing.id

    token = create_token(email, role , user_id, timedelta(minutes=20))
    return {"access_token" : token, "token_type" : "bearer"}



@customer_router.get("/details", status_code=status.HTTP_200_OK)
async def get_details(user_details : user_dependency, db : db_dependency):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    query = select(Customer).where(Customer.user_id == user_id)

    result = await db.execute(query)

    customer_details = result.scalar_one_or_none()

    if customer_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer Not Found")

    details = Customer_details_model.model_validate({
        "first_name" : customer_details.first_name,
        "last_name" : customer_details.last_name,
        "address" : customer_details.address,
        "phone_number" : customer_details.phone_number,
        "email" : customer_details.user_details.email
    })

    return details



@customer_router.put("/change_password",status_code=status.HTTP_202_ACCEPTED)
async def change_password(user_details : user_dependency, db : db_dependency, password : Password_Change_model):
    user_id = user_details.get("id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    query = select(Users).where(Users.id == user_id)

    result = await db.execute(query)

    query_result = result.scalar_one_or_none()

    if query_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Customer Not Found")

    old_password = query_result.hashed_password

    verification = verify_password_hash(old_password, password.old_password)

    if not verification:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Password does nor match")

    new_password = await run_in_threadpool(hash_password, password.new_password)

    query_result.hashed_password = new_password

    try:
        await db.flush()
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Failed to update Password")

    return {"detail" : "Password Changed Successfuly"}