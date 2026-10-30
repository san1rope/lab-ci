from dataclasses import dataclass
from typing import Protocol


class RateProvider(Protocol):
    """Джерело курсів валют: скільки гривень коштує 1 одиниця валюти."""

    def get_rate(self, currency: str) -> float: ...


@dataclass
class Item:
    name: str
    price: float
    qty: int


class Cart:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def add(self, name: str, price: float, qty: int = 1) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self._items:
            self._items[name].qty += qty
        else:
            self._items[name] = Item(name, price, qty)

    def remove(self, name: str) -> None:
        if name not in self._items:
            raise KeyError(name)
        del self._items[name]

    def items_count(self) -> int:
        return sum(item.qty for item in self._items.values())

    def total(self, discount_percent: float = 0) -> float:
        if not 0 <= discount_percent <= 100:
            raise ValueError("discount_percent must be in [0, 100]")
        subtotal = sum(item.price * item.qty for item in self._items.values())
        return round(subtotal * (1 - discount_percent / 100), 2)

    def total_in(self, currency: str, rates: RateProvider) -> float:
        rate = rates.get_rate(currency)
        if rate <= 0:
            raise ValueError("rate must be positive")
        return round(self.total() / rate, 2)