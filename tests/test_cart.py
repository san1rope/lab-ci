from unittest.mock import Mock

import pytest

from shop.cart import Cart, Item


class FixedRates:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def get_rate(self, currency: str) -> float:
        return self.rate


def test_new_cart_is_empty(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0


def test_add_new_item(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0, qty=3)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 600.0


def test_add_same_item_increases_qty(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0)
    empty_cart.add("book", price=200.0, qty=2)
    assert empty_cart.items_count() == 3


def test_add_same_name_different_price_keeps_first_price(empty_cart: Cart) -> None:
    # Рішення: товар ідентифікується за назвою, ціна береться з першого додавання
    empty_cart.add("book", price=200.0)
    empty_cart.add("book", price=300.0)
    assert empty_cart.items_count() == 2
    assert empty_cart.total() == 400.0


def test_add_zero_price_allowed(empty_cart: Cart) -> None:
    empty_cart.add("gift", price=0.0)
    assert empty_cart.items_count() == 1
    assert empty_cart.total() == 0


def test_items_count(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_total_without_discount(cart_with_items: Cart) -> None:
    assert cart_with_items.total() == 460.0


@pytest.mark.parametrize(
    ("discount", "expected"),
    [(0, 460.0), (10, 414.0), (50, 230.0), (100, 0.0)],
)
def test_total_with_discount(cart_with_items: Cart, discount: float, expected: float) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected)


def test_remove_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("pen")
    assert cart_with_items.items_count() == 2


@pytest.mark.parametrize("price", [-1.0, -0.01])
def test_add_negative_price_raises(empty_cart: Cart, price: float) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("book", price=price)


@pytest.mark.parametrize("qty", [0, -1])
def test_add_non_positive_qty_raises(empty_cart: Cart, qty: int) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", price=100.0, qty=qty)


@pytest.mark.parametrize("discount", [-1, -0.01, 100.01, 150])
def test_total_invalid_discount_raises(cart_with_items: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart_with_items.total(discount_percent=discount)


def test_remove_missing_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("book")


def test_total_in_with_mock(empty_cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0  # 1 USD = 40 UAH
    empty_cart.add("book", price=400.0)
    assert empty_cart.total_in("USD", rates) == 10.0
    rates.get_rate.assert_called_once_with("USD")


def test_total_in_with_stub(cart_with_items: Cart) -> None:
    assert cart_with_items.total_in("USD", FixedRates(40.0)) == 11.5


@pytest.mark.parametrize("rate", [0.0, -5.0])
def test_total_in_invalid_rate_raises(cart_with_items: Cart, rate: float) -> None:
    with pytest.raises(ValueError, match="rate"):
        cart_with_items.total_in("USD", FixedRates(rate))


def test_most_expensive_empty_cart_returns_none(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_by_unit_price_not_by_sum(empty_cart: Cart) -> None:
    empty_cart.add("pen", price=15.0, qty=100)
    empty_cart.add("book", price=200.0, qty=1)
    result = empty_cart.most_expensive()
    assert result is not None
    assert result.name == "book"


def test_most_expensive_single_item(empty_cart: Cart) -> None:
    empty_cart.add("pen", price=15.0)
    assert empty_cart.most_expensive() == Item("pen", 15.0, 1)
