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


def register_admin_without_user_id(setup_database, override_get_db):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid Token"}


def test_register_admin_without_users(setup_database, override_get_db, override_get_admin):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmintest".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Admin Not Found"}


def test_register_admin_with_duplicate_emails(setup_database, override_get_db, setup_admin_data, override_get_admin):
    response = client.post("/admin/registration", json = {"email" : "exampleAdmin".lower(), "password" : "exampleAdmin", "first_name" : "exampleAdmin", "last_name" : "admin", "phone_number" : "9876543211", "address" : "street"})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail" : "Email Already Registered"}