from enum import Enum

class HoldingType(Enum):
    OTHER = 0
    ETF = 1


class Holding:
    def __init__(
        self, symbol: str, type: HoldingType, price: float = 0, value: float = 0
    ):
        self.symbol = symbol
        self.type = type
        self.price = price
        self.value = value
