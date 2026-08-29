from pydantic import BaseModel


class OrderCreate(BaseModel):
    restaurant_id: str
    item_id: str
    quantity: int


class OrderOut(BaseModel):
    id: str
    restaurant_id: str
    item_id: str
    quantity: int
    total_price: float
    status: str


# Mirrors the shape of restaurant-service's MenuItem, as returned over REST.
# order-service never touches restaurant-service's database directly.
class MenuItemDTO(BaseModel):
    id: str
    restaurant_id: str
    name: str
    price: float
    available: bool
