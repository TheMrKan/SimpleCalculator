from typing import Callable
import operator as ops
from functools import wraps


class OperationError(Exception):
    left: float
    right: float
    operator: str
    comment: str | None

    def __init__(self, left: float, operator: str, right: float, comment: str | None = None) -> None:
        self.left = left
        self.operator = operator
        self.right = right
        self.comment = comment

    def __str__(self) -> str:
        return f"Недопустимая операция: {self.left} {self.operator} {self.right}{f" - {self.comment}" if self.comment else ""}"


class BinaryOperator:
    __func: Callable[[float, float], float]
    __str_repr: str

    @classmethod
    def from_symbol(cls, sym: str):
        return _OP_MAP[sym]

    def __init__(self, str_repr: str, func: Callable[[float, float], float]):
        self.__func = func
        self.__str_repr = str_repr

    def __call__(self, left: float, right: float) -> float:
        try:
            return round(float(self.__func(left, right)), 2)
        except OperationError as e:
            e.operator = self.__str_repr
            raise
        except OverflowError as e:
            raise OperationError(left, self.__str_repr, right, "переполнение") from e

    def __str__(self) -> str:
        return self.__str_repr

    def __repr__(self) -> str:
        return self.__str_repr


def assert_right_is_non_zero(func: Callable[[float, float], float]) -> Callable[[float, float], float]:
    @wraps(func)
    def wrapper(left: float, right: float) -> float:
        if right == 0:
            raise OperationError(left, "", right, "деление на ноль")
        return func(left, right)

    return wrapper


def assert_right_is_integer(func: Callable[[float, float], float]) -> Callable[[float, float], float]:
    @wraps(func)
    def wrapper(left: float, right: float) -> float:
        if not right.is_integer():
            raise OperationError(left, "", right, "операция допустима только над целым числом")
        return func(left, right)
    return wrapper


_OP_MAP = {
    "+": BinaryOperator("+", ops.add),
    "-": BinaryOperator("-", ops.sub),
    "*": BinaryOperator("*", ops.mul),
    "/": BinaryOperator("/", assert_right_is_non_zero(ops.truediv)),
    "#": BinaryOperator("//", assert_right_is_non_zero(assert_right_is_integer(ops.floordiv))),
    "%": BinaryOperator("%", assert_right_is_integer(ops.mod)),
    "^": BinaryOperator("**", ops.pow),
}
