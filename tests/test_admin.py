from tests.utils import *
from main import app
from starlette import status



def test_register_admin(setup_database, override_get_db, setup_admin_data, override_get_admin):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail" : "Admin Created"}


def test_register_admin_with_customer_role(setup_database, override_get_db, setup_admin_data, override_get_customer):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail":"Only Authorized for Admins"} 


def test_register_admin_without_jwt(setup_database, override_get_db):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_register_admin_without_users(setup_database, override_get_db, override_get_admin):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Admin Not Found"}


def test_register_admin_with_duplicate_emails(setup_database, override_get_db, setup_admin_data, override_get_admin):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmin".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail" : "Email Already Registered"}


def test_login(setup_database, override_get_db, setup_admin_data):
    response = client.post("/admin/admin_login", data = {"username" : "exampleAdmin".lower(), "password" : "exampleAdmin"})
    assert response.status_code == status.HTTP_200_OK


def test_login_with_wrong_email_and_password(setup_database, override_get_db, setup_admin_data):
    response = client.post("/admin/admin_login", data = {"username" : "exampleAdminss".lower(), "password" : "exampleAdmin"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post("/admin/admin_login", data = {"username" : "exampleAdmin".lower(), "password" : "exampleAdmin123"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_sellers(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_admin):
    response = client.get("/admin/get_sellers")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["user_id"] == "userseller_test_1"


def test_get_sellers_with_limit_and_skip(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_admin):
    response = client.get("/admin/get_sellers", params = {"limit" : 100, "skip" : 20})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_sellers_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_customer):
    response = client.get("/admin/get_sellers")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid Token"}


def test_get_sellers_with_no_jwt(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_customer):
    response = client.get("/admin/get_sellers")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid Token"}


def test_get_sellers_with_no_user(setup_database, override_get_db, setup_seller_data, override_get_admin):
    response = client.get("/admin/get_sellers")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Admin Not Found"}


def test_get_sellers_with_admin_not_in_db(setup_database, override_get_db, setup_seller_data, setup_admin_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_admin_role
    response = client.get("/admin/get_sellers")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid User"}
    app.dependency_overrides.pop(token_bearer, None)


def test_get_seller_by_seller_id(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_admin):
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "seller_test_1"


def test_get_seller_by_seller_id_with_no_jwt(setup_database, override_get_db, setup_seller_data, setup_admin_data):
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_get_seller_by_seller_id_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_admin_data, override_get_customer):
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid Token"}


def test_get_seller_by_seller_id_with_no_admin_in_db(setup_database, override_get_db, setup_seller_data, override_get_admin):
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Admin Not Found"}


def test_get_seller_by_seller_id_admin_not_in_db(setup_database, override_get_db, setup_seller_data, setup_admin_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_admin_role
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid User"}
    app.dependency_overrides.pop(token_bearer, None)


def test_get_seller_by_seller_id_with_noseller(setup_database, override_get_db, setup_admin_data, override_get_admin):
    response = client.get("/admin/get_seller/seller_test_1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Seller Not Found"}