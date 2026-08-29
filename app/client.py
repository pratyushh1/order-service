import os
import requests
from app.schemas import MenuItemDTO

RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8081")


def get_menu_item(item_id: str) -> MenuItemDTO | None:
    """Calls restaurant-service over REST to fetch a menu item.
    This is the loose-coupling communication pattern: order-service never
    reads restaurant-service's database directly.
    """
    try:
        response = requests.get(f"{RESTAURANT_SERVICE_URL}/menu/{item_id}", timeout=5)
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach restaurant-service: {e}") from e

    if response.status_code == 404:
        return None
    response.raise_for_status()
    return MenuItemDTO(**response.json())
