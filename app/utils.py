from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"'{id_str}' is not a valid id")


def serialize_order(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "restaurant_id": doc["restaurant_id"],
        "item_id": doc["item_id"],
        "quantity": doc["quantity"],
        "total_price": doc["total_price"],
        "status": doc["status"],
    }
