from tests.utils import *
from starlette import status


def test_add_products(setup_database, override_get_db, setup_seller_data, override_get_seller):
    response = client.post("/products/add_products", json = {"product_name" : "Test Product 1", "product_description" : "Product for testing", "price" : 10, "stock" : 20})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail" : "Product Added"}


def test_add_products_with_lessthan_zero_stock(setup_database, override_get_db, setup_seller_data, override_get_seller):
    response = client.post("/products/add_products", json = {"product_name" : "Test Product 1", "product_description" : "Product for testing", "price" : -1, "stock" : 0})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_products_with_withless_zero_price(setup_database, override_get_db, setup_seller_data, override_get_seller):
    response = client.post("/products/add_products", json = {"product_name" : "Test Product 1", "product_description" : "Product for testing", "price" : 0, "stock" : -1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_product_with_customer_role(setup_database, override_get_db, setup_seller_data, override_get_customer):
    response = client.post("/products/add_products", json = {"product_name" : "Test Product 1", "product_description" : "Product for testing", "price" : 0, "stock" : 0})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "User is Not a Seller"}


def test_add_product_with_no_auth_token(setup_database, override_get_db, setup_seller_data):
    response = client.post("/products/add_products", json = {"product_name" : "Test Product 1", "product_description" : "Product for testing", "price" : 0, "stock" : 0})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_modify_products_with_product_name(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("/products/modify_products/product_test_1", json={"product_name" : "Product_test_change_1"})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Product Modified"}


def test_modify_products_with_product_description(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("/products/modify_products/product_test_1", json={"product_description" : "product_test_description_change"})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Product Modified"}


def test_modify_products(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("/products/modify_products/product_test_1", json={"product_name" : "Product_test_change_1", "product_description" : "product_test_description_change"})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Product Modified"}


def test_modify_product(setup_database, override_get_db, setup_seller_data, setup_product_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_seller_role
    response = client.put("/products/modify_products/product_test_1", json={"product_name" : "Product_test_change_1", "product_description" : "product_test_description_change"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not the seller of this product"}


def test_modify_products_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_customer):
    response = client.put("/products/modify_products/product_test_1", json={"product_name" : "Product_test_change_1", "product_description" : "product_test_description_change"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "User is Not a Seller"}


def test_modify_products_with_no_auth_token(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.put("/products/modify_products/product_test_1", json={"product_name" : "Product_test_change_1", "product_description" : "product_test_description_change"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_list_products(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_customer):
    response = client.get("/products/list_products")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["product_name"] == "Test_Product_1"
    assert response.json()[1]["product_name"] == "Test_Product_2"


def test_list_products_with_no_auth(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.get("/products/list_products")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_increase_stock(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/increase_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Quantity Increased"}


def test_increase_stock_with_another_seller_id(setup_database, override_get_db, setup_seller_data, setup_product_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_seller_role
    response = client.put("products/increase_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not the seller of this product"}


def test_increase_stock_with_no_product(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/increase_stock/No_product", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Product Not Found"}


def test_increase_stock_with_no_auth_token(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.put("products/increase_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_increase_stock_with_less_than_zero(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/increase_stock/product_test_1", params = {"quantity" : -10})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_increase_stock_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_customer):
    response = client.put("products/increase_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "User is not a seller"}


def test_decrease_stock(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/decrease_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Quantity Decreased"}


def test_decrease_stock_with_another_seller_id(setup_database, override_get_db, setup_seller_data, setup_product_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_seller_role
    response = client.put("products/decrease_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not the seller of this product"}


def test_decrease_stock_with_no_product(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/decrease_stock/No_product", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Product Not Found"}


def test_decrease_stock_with_no_auth_token(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.put("products/decrease_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_decrease_stock_with_less_than_zero(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/decrease_stock/product_test_1", params = {"quantity" : -10})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_decrease_stock_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_customer):
    response = client.put("products/decrease_stock/product_test_1", params = {"quantity" : 10})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "User is not a seller"}


def test_change_price(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/change_price/product_test_1", params = {"new_price" : 67})
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail" : "Price Changed"}


def test_change_price_with_another_seller(setup_database, override_get_db, setup_seller_data, setup_product_data):
    app.dependency_overrides[token_bearer] = override_get_current_user_with_seller_role
    response = client.put("products/change_price/product_test_1", params = {"new_price" : 67})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "You are not the seller of this product"}


def test_change_price_with_customer_role(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_customer):
    response = client.put("products/change_price/product_test_1", params = {"new_price" : 67})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail" : "User is not a seller"}


def test_change_price_with_no_product(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/change_price/No_product", params = {"new_price" : 67})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail" : "Product Not Found"}


def test_change_price_with_no_auth(setup_database, override_get_db, setup_seller_data, setup_product_data):
    response = client.put("products/change_price/product_test_1", params = {"new_price" : 67})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail" : "Not authenticated"}


def test_change_price_to_negative(setup_database, override_get_db, setup_seller_data, setup_product_data, override_get_seller):
    response = client.put("products/change_price/product_test_1", params = {"new_price" : -67})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT