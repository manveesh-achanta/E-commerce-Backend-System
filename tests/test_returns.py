from tests.utils import *
from main import app
from starlette import status


def test_return_order(setup_database, setup_order_data, override_get_db, override_get_customer):
    response = client.post("/return/return_order/order_test_1", json = {"reason_for_return" : "Test Return"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail" : "Return Sucessfull"}


def test_return_order_with_seller_role(setup_database, setup_order_data, override_get_db, override_get_seller):
    response = client.post("/return/return_order/order_test_1", json = {"reason_for_return" : "Test Return"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not the customer"}


def test_return_order_with_no_auth(setup_database, setup_order_data, override_get_db):
    response = client.post("/return/return_order/order_test_1", json = {"reason_for_return" : "Test Return"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_return_order_with_customer_not_in_db(setup_database, setup_order_data, override_get_db):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_customer_role
    response = client.post("/return/return_order/order_test_1", json = {"reason_for_return" : "Test Return"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "User Not Found"}


def test_change_return_status(setup_database, setup_order_data, override_get_db, override_get_seller, setup_return_data):
    response = client.put("/return/change_return_status/return_test_1", params = {"new_return_status" : "approved"})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Status Update Done"}


def test_change_return_status_with_customer_role(setup_database, setup_order_data, override_get_db, override_get_customer, setup_return_data):
    response = client.put("/return/change_return_status/return_test_1", params = {"new_return_status" : "approved"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not allowed to change the status"}


def test_change_return_status_for_no_returns(setup_database, setup_order_data, override_get_db, override_get_seller, setup_return_data):
    response = client.put("/return/change_return_status/No_Return", params = {"new_return_status" : "approved"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "No Returns Found"}


def test_returns_of_customers(setup_database, setup_order_data, override_get_db, setup_return_data, override_get_customer):
    response = client.get("/return/get_returns")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == "return_test_1"


def test_returns_of_customer_with_no_auth_token(setup_database, setup_order_data, override_get_db, setup_return_data):
    response = client.get("/return/get_returns")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}