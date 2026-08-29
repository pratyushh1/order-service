from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError
import time

from app.database import orders_collection, client as mongo_client
from app import schemas, client
from app.utils import to_object_id, serialize_order

app = FastAPI(title="order-service")


@app.on_event("startup")
def on_startup():
    last_error = None
    for attempt in range(10):
        try:
            mongo_client.admin.command("ping")
            return
        except PyMongoError as e:
            last_error = e
            time.sleep(3)
    raise RuntimeError(f"Could not connect to MongoDB after retries: {last_error}")


@app.get("/health")
def health():
    return {"status": "order-service is up"}


@app.post("/orders", response_model=schemas.OrderOut)
def create_order(order_request: schemas.OrderCreate):
    # 1. Ask restaurant-service for the menu item's details over REST.
    try:
        item = client.get_menu_item(order_request.item_id)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if item is None:
        raise HTTPException(status_code=400, detail=f"Menu item {order_request.item_id} not found")
    if not item.available:
        raise HTTPException(status_code=400, detail=f"Menu item {order_request.item_id} is unavailable")
    if item.restaurant_id != order_request.restaurant_id:
        raise HTTPException(
            status_code=400,
            detail=f"Menu item {order_request.item_id} does not belong to restaurant {order_request.restaurant_id}",
        )

    # 2. Save the order in order-service's OWN MongoDB database.
    order_doc = {
        "restaurant_id": order_request.restaurant_id,
        "item_id": order_request.item_id,
        "quantity": order_request.quantity,
        "total_price": item.price * order_request.quantity,
        "status": "PLACED",
    }
    result = orders_collection.insert_one(order_doc)
    doc = orders_collection.find_one({"_id": result.inserted_id})
    return serialize_order(doc)


@app.get("/orders", response_model=list[schemas.OrderOut])
def list_orders():
    return [serialize_order(doc) for doc in orders_collection.find()]


# THIS IS THE ENDPOINT delivery-service calls to confirm an order exists.
@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: str):
    try:
        oid = to_object_id(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = orders_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(doc)
