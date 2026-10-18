from tests.utils import *
from main import app
from starlette import status



def test_create_seller(override_get_db, setup_database):
    response_1 = client.post("/seller/create_seller", json={"email" : "exampleSeller@123.com", "password" : "examplesellerpassword", "first_name" : "exampleseller", "last_name" : "seller" , "phone_number" : "987654321" , "address" : "street" , "store_name" : "sellerstore"})
    assert response_1.status_code == status.HTTP_201_CREATED


def test_create_seller_with_duplicate_username(override_get_db, setup_database, setup_seller_data):
    response = client.post("/seller/create_seller", json={"email" : "exampleSeller", "password" : "examplesellerpassword", "first_name" : "exampleseller", "last_name" : "seller" , "phone_number" : "987654321" , "address" : "street" , "store_name" : "sellerstore"})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_seller_with_invalid_data(override_get_db, setup_database):
    response = client.post("/seller/create_seller", json={"email" : "exampleSeller@123.com", "password" : "examplesellerpassword", "first_name" : "exampleseller", "last_name" : "seller" , "phone_number" : 987654321 , "address" : "street" , "store_name" : "sellerstore"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_seller_login(override_get_db, setup_database, setup_seller_data, setup_customer_data):
    response = client.post("/seller/seller_login", data = {"username" : "exampleSeller".lower(), "password" : "exampleSeller"})
    assert response.status_code == status.HTTP_200_OK


def test_seller_login2(override_get_db, setup_database, setup_seller_data, setup_customer_data):
    response = client.post("/seller/seller_login", data = {"username" : "exampleSellerss".lower(), "password" : "exampleSeller"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_seller_login1(override_get_db, setup_database, setup_seller_data, setup_customer_data):
    response = client.post("/seller/seller_login", data = {"username" : "exampleSeller".lower(), "password" : "exampleSeller123"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_seller_login3(override_get_db, setup_database, setup_seller_data, setup_customer_data):
    response_4 = client.post("/seller/seller_login", data = {"username" : "exampleCustomer".lower(), "password" : "exampleeeeCustomer"})
    assert response_4.status_code == status.HTTP_403_FORBIDDEN


def test_get_details(override_get_db, setup_database, setup_seller_data, override_get_seller):
    response = client.get("/seller/details")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "exampleSeller".lower()


def test_get_details_with_customer_role(override_get_db, setup_database, setup_seller_data, override_get_customer):
    response_3 = client.get("/seller/details")
    assert response_3.status_code == status.HTTP_403_FORBIDDEN


def test_get_details_with_admin_role(override_get_db, setup_database, setup_seller_data, override_get_admin):
    response_3 = client.get("/seller/details")
    assert response_3.status_code == status.HTTP_403_FORBIDDEN


def test_get_products(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_seller):
    response = client.get("/seller/get_products")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["product_name"] == "Test_Product_1"
    assert response.json()[1]["product_name"] == "Test_Product_2"


def test_get_products_with_customer_role(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_customer):
    response = client.get("/seller/get_products")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_products_with_admin_role(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_admin):
    response = client.get("/seller/get_products")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_products_with_no_id(override_get_db, setup_database, setup_seller_data, setup_product_data):
    response = client.get("/seller/get_products")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_seller):
    response_1 = client.put("/seller/change_password", json = {"old_password" : "exampleSeller", "new_password" : "exampleSeller123"})
    assert response_1.status_code == status.HTTP_202_ACCEPTED
    assert response_1.json() == {"detail" : "Password Changed Successfuly"}


def test_change_password_with_wrong_password(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_seller):
    response_1 = client.put("/seller/change_password", json = {"old_password" : "exampleSeller123", "new_password" : "exampleSeller123"})
    assert response_1.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password_with_customer_role(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_customer):
    response_2 = client.put("/seller/change_password", json = {"old_password" : "exampleSeller", "new_password" : "exampleSeller123"})
    assert response_2.status_code == status.HTTP_403_FORBIDDEN


def test_change_password_with_admin_role(override_get_db, setup_database, setup_seller_data, setup_product_data, override_get_admin):
    response_2 = client.put("/seller/change_password", json = {"old_password" : "exampleSeller", "new_password" : "exampleSeller123"})
    assert response_2.status_code == status.HTTP_403_FORBIDDEN


def test_get_orders(override_get_db, setup_database, setup_seller_data, setup_product_data, setup_order_data, override_get_seller):
    response_1 = client.get("/seller/get_orders")
    assert response_1.status_code == status.HTTP_200_OK

def test_get_orders_with_customer_role(override_get_db, setup_database, setup_seller_data, setup_product_data, setup_order_data, override_get_customer):
    response_2 = client.get("/seller/get_orders")
    assert response_2.status_code == status.HTTP_403_FORBIDDEN


def test_get_orders_with_no_user_id(override_get_db, setup_database, setup_seller_data, setup_product_data, setup_order_data):
    response_3 = client.get("/seller/get_orders")
    assert response_3.status_code == status.HTTP_401_UNAUTHORIZED