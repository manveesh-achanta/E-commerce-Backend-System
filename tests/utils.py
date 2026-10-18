from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from fastapi.testclient import TestClient
from main import app
import pytest
import pytest_asyncio
from models import Users, Returns, Orders, Seller, Admin, Customer, UserRole, Products, OrderStatus, ReturnStatus
from core.security import hash_password
from dependencies.token_dependency import token_bearer
from dependencies.database_dependency import get_db



SQLALCHEMY_DATABSE_URL = "sqlite+aiosqlite:///./testing.db"



test_engine = create_async_engine(
    SQLALCHEMY_DATABSE_URL,
    connect_args={"check_same_thread" : False},
    poolclass=StaticPool,
)



Testing_Session_local = async_sessionmaker(autocommit = False, autoflush = False, bind=test_engine, expire_on_commit = False)



async def get_db_temp():
    db = Testing_Session_local()
    try:
        yield db
    finally:
        await db.close()



async def override_get_current_admin():
    return {"username" : "exampleAdmin", "id" : "useradmin_test_1", "role" : UserRole.ADMIN}

async def override_get_current_customer():
    return {"username" : "exampleCustomer", "id" : "usercustomer_test_1", "role" : UserRole.CUSTOMER}

async def override_get_current_seller():
    return {"username" : "exampleSeller", "id" : "userseller_test_1", "role" : UserRole.SELLER}



client = TestClient(app=app)



@pytest_asyncio.fixture
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)



@pytest_asyncio.fixture
async def setup_admin_data(setup_database):

    user = Users(
        id = "useradmin_test_1",
        email = "exampleAdmin".lower(),
        hashed_password = hash_password("exampleAdmin"),
        role = UserRole.ADMIN
    )

    admin = Admin(
        id = "admin_test_1",
        first_name = "exampleAdmin",
        last_name = "admin",
        phone_number = "9876543211",
        address = "street",
        user_detail = user
    )

    db = Testing_Session_local()
    db.add_all([user, admin])
    await db.commit()
    await db.close()
    yield user, admin



@pytest_asyncio.fixture
async def setup_customer_data(setup_database):

    user = Users(
        id = "usercustomer_test_1",
        email = "exampleCustomer".lower(),
        hashed_password = hash_password("exampleCustomer"),
        role = UserRole.CUSTOMER       
    )

    customer = Customer(
        id = "customer_test_1",
        first_name = "exampleCustomer",
        last_name = "Customer",
        phone_number = "9876543211",
        address = "street",
        user_details = user
    )

    db = Testing_Session_local()
    db.add_all([user, customer])
    await db.commit()
    yield user, customer



@pytest_asyncio.fixture
async def setup_seller_data():

    user = Users(
        id = "userseller_test_1",
        email = "exampleSeller".lower(),
        hashed_password = hash_password("exampleSeller"),
        role = UserRole.SELLER
    )

    seller = Seller(
        id = "seller_test_1",
        first_name = "exampleSeller",
        last_name = "Seller",
        phone_number = "9876543211",
        address = "street",
        store_name = "exampleStore",
        user_details = user
    )

    db = Testing_Session_local()
    db.add_all([user, seller])
    await db.commit()
    await db.close()
    yield user, seller



@pytest_asyncio.fixture
async def setup_product_data(setup_seller_data):

    product_1 = Products(
        id = "product_test_1",
        seller_id = "seller_test_1",
        product_name = "Test_Product_1",
        product_description = "Test_product_description_1",
        price = 10,
        stock  = 12
    )

    product_2 = Products(
        id = "product_test_2",
        seller_id = "seller_test_1",
        product_name = "Test_Product_2",
        product_description = "Test_product_description_2",
        price = 13,
        stock  = 10
    )

    db = Testing_Session_local()
    db.add_all([product_1, product_2])
    await db.commit()
    await db.close()
    yield product_1, product_2



@pytest_asyncio.fixture
async def setup_order_data(setup_customer_data, setup_product_data):

    _ , customer = setup_customer_data
    product_1, _ = setup_product_data

    order_model = Orders(
        id = "order_test_1",
        seller_id = product_1.seller_id,
        customer_id = customer.id,
        product_id = product_1.id,
        price = product_1.price,
        order_status = OrderStatus.PACKING,
        delivered_at = None
    )

    db = Testing_Session_local()
    db.add(order_model)
    await db.commit()
    await db.close()
    yield order_model



@pytest_asyncio.fixture
async def setup_return_data(setup_customer_data, setup_order_data):

    _ , customer = setup_customer_data
    order = setup_order_data

    return_model = Returns(
        id = "return_test_1",
        customer_id = customer.id,
        order_id = order.id,
        reason = "Testing the API",
        return_status = ReturnStatus.RETURN_REQUESTED
    )

    db = Testing_Session_local()
    db.add(return_model)
    await db.commit()
    await db.close()
    yield return_model



@pytest_asyncio.fixture
async def override_get_customer():
    app.dependency_overrides[token_bearer] = override_get_current_customer
    yield
    app.dependency_overrides.pop(token_bearer, None)



@pytest_asyncio.fixture
async def override_get_admin():
    app.dependency_overrides[token_bearer] = override_get_current_admin
    yield
    app.dependency_overrides.pop(token_bearer, None)



@pytest_asyncio.fixture
async def override_get_seller():
    app.dependency_overrides[token_bearer] = override_get_current_seller
    yield
    app.dependency_overrides.pop(token_bearer, None)



@pytest.fixture
def override_get_db():
    app.dependency_overrides[get_db] = get_db_temp
    yield
    app.dependency_overrides.pop(get_db, None)