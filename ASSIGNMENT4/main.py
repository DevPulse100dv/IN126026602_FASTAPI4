from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# -----------------------
# Home Route
# -----------------------
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI Cart System"}


# -----------------------
# Product Database
# -----------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]


# -----------------------
# Storage
# -----------------------
cart = []
orders = []
order_counter = 1


# -----------------------
# Helper Function
# -----------------------
def calculate_total(product, qty):
    return product["price"] * qty


# -----------------------
# Add to Cart
# -----------------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    # Quantity validation
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Find product
    product = next((p for p in products if p["id"] == product_id), None)

    # Product not found
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Out of stock
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # Check duplicate product in cart
    for item in cart:
        if item["product_id"] == product_id:

            item["quantity"] += quantity
            item["subtotal"] = calculate_total(
                product,
                item["quantity"]
            )

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # New cart item
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }


# -----------------------
# View Cart
# -----------------------
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# -----------------------
# Remove Item
# -----------------------
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:

            cart.remove(item)

            return {
                "message": "Product removed from cart"
            }

    raise HTTPException(
        status_code=404,
        detail="Item not found in cart"
    )


# -----------------------
# Checkout Request Model
# -----------------------
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# -----------------------
# Checkout
# -----------------------
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_counter

    # Empty cart check
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    grand_total = sum(item["subtotal"] for item in cart)

    created_orders = []

    # Create orders
    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        created_orders.append(order)

        order_counter += 1

    # Clear cart after checkout
    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": created_orders,
        "grand_total": grand_total
    }


# -----------------------
# View Orders
# -----------------------
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }
