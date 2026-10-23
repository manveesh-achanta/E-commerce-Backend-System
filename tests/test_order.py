from tests.utils import *
from starlette import status


def test_place_order(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, override_get_customer):
    response = client.post("/order/place_order/product_test_1")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail" : "Order Placed"}


def test_place_order_with_no_token(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.post("/order/place_order/product_test_1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_place_order_with_customer_not_in_db(setup_database, override_get_db, setup_seller_data, setup_product_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_customer_role
    response = client.post("/order/place_order/product_test_1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Customer profile not found"}


def test_palce_order_with_product_not_in_db(setup_database, override_get_db, setup_seller_data, setup_customer_data, override_get_customer):
    response = client.post("/order/place_order/no_product")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Product Not Found"}


def test_place_order_with_stock_zero(setup_database, override_get_db, setup_customer_data, setup_seller_data, setup_product_data, override_get_customer):
    response = client.post("/order/place_order/product_test_2")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail" : "Product is out of stock."}


def test_change_status(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, override_get_seller, setup_order_data):
    response = client.put("/order/change_status/order_test_1", params = {"status_update" : "shipping"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail" : "Status Changed"}


def test_change_status_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, override_get_customer, setup_order_data):
    response = client.put("/order/change_status/order_test_1", params = {"status_update" : "shipping"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Invalid Token"}


def test_change_status_with_no_orders(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, override_get_seller):
    response = client.put("/order/change_status/order_test_1", params = {"status_update" : "shipping"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Order Not Found"}


def test_change_status_with_no_auth_token(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data):
    response = client.put("/order/change_status/order_test_1", params = {"status_update" : "shipping"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_get_status(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_customer):
    response = client.get("/order/get_status/order_test_1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Order Status" : "packing"}


def test_get_status_with_no_order_id(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_customer):
    response = client.get("/order/get_status/No_Order_ID")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Order Not Found"}


def test_cancel_order_by_customer(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_customer):
    response = client.put("/order/cancel_order/order_test_1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail" : "Order Cancelled by Customer"}


def test_cancel_order_by_seller(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_seller):
    response = client.put("/order/cancel_order/order_test_1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail" : "Order Cancelled by Seller"}


def test_cancel_order_by_admin(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_admin):
    response = client.put("/order/cancel_order/order_test_1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail" : "Order Cancelled by Admin"}


def test_cancel_order_with_order_not_in_db(setup_database, override_get_db, setup_seller_data, setup_customer_data, setup_product_data, setup_order_data, override_get_customer):
    response = client.put("/order/cancel_order/No_Order")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Order Not Found"}