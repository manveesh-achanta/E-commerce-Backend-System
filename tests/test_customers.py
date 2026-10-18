from tests.utils import *
from main import app
from starlette import status



def test_create_customer(setup_database, override_get_db):
    response = client.post("/customer/create_customer", json = {"first_name" : "Example Test User 1", "last_name" : "example last name", "email" : "email@123.com", "password" : "examplepassword", "phone_number" : "9492666432", "address" : "street"})
    assert response.status_code == status.HTTP_201_CREATED


def test_create_customer_with_duplicate_username(setup_database, override_get_db, setup_customer_data):
    response = client.post("/customer/create_customer", json = {"first_name" : "Example Test User 1", "last_name" : "example last name", "email" : "exampleCustomer", "password" : "examplepassword", "phone_number" : "9492666432", "address" : "street"})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_customer_login(setup_customer_data, override_get_customer, override_get_db):
    response = client.post("/customer/customer_login", data = {"username" : "exampleCustomer", "password" : "exampleCustomer"})
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_customer_login_wrong_email_and_password(override_get_db, setup_customer_data, override_get_customer):
    response = client.post("/customer/customer_login", data = {"username" : "exampleCustomer", "password" : "exampleeeeCustomer"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = client.post("/customer/customer_login", data = {"username" : "exampleeeeCustomer", "password" : "exampleCustomer"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_details(setup_customer_data, override_get_customer, override_get_db):
    response = client.get("/customer/details")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "exampleCustomer"
    assert response.json()["last_name"] == "Customer"


def test_get_details_with_seller(override_get_db, setup_customer_data, override_get_seller):
    response = client.get("/customer/details")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_details_with_no_user_id(override_get_db):
    app.dependency_overrides.pop(token_bearer, None)
    response = client.get("/customer/details")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password(setup_customer_data, override_get_customer, override_get_db):
    response = client.put("/customer/change_password", json = {"old_password" : "exampleCustomer", "new_password" : "exampleCustomerPassword"})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Password Changed Successfuly"}


def test_change_passowrd_using_wrong_password(setup_customer_data, override_get_customer, override_get_db):
    response = client.put("/customer/change_password", json = {"old_password" : "exampleCustomer1234", "new_password" : "exampleCustomerPassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Password does not match"}