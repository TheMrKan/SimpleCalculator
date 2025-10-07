from typing import Callable
import operator as ops
from functools import wraps


class OperationError(Exception):
    """
    Ошибка при выполнении оператора
    """

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
        """
        Считается в функции, т. к. comment может присваиваться после инициализации
        """
        return f"Недопустимая операция: {self.left} {self.operator} {self.right}{f" - {self.comment}" if self.comment else ""}"


class BinaryOperator:
    """
    Предполагается, что экземпляр оператора создается один раз и дальше используется как Flyweight через from_symbol.
    Экземпляр оператора является callable, т. е. используется как op_instance(left, right).
    """
    __func: Callable[[float, float], float]
    __str_repr: str
    """
    Строковое представление оператора для отладки и вывода ошибок
    """

    @staticmethod
    def from_symbol(sym: str) -> 'BinaryOperator':
        """
        Для получения экземпляра оператора по символу
        :raises KeyError: Оператор не определен
        :return: Flyweight экземпляр оператора
        """
        return _OP_MAP[sym]

    def __init__(self, str_repr: str, func: Callable[[float, float], float]):
        self.__func = func
        self.__str_repr = str_repr

    def __call__(self, left: float, right: float) -> float:
        """
        Применяет оператор, аналог 'left ? right', где ? - оператор (например +).
        Все вычисления проводятся над float.
        :raises OperationError: Если произошла заранее обработанная ошибка (например, переполнение)
        :return: Результат выполнения с точностью 2 знака после запятой
        """
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
    """
    Декоратор, проверяющий, что правый операнд не ноль.
    :raises OperationError: Правой операнд 0
    """
    @wraps(func)
    def wrapper(left: float, right: float) -> float:
        if right == 0:
            raise OperationError(left, "", right, "деление на ноль")
        return func(left, right)

    return wrapper


def assert_integers(func: Callable[[float, float], float]) -> Callable[[float, float], float]:
    """
    Декоратор, проверяющий, что оба операнда - целые числа.
    :raises OperationError: Хотя бы один из операндов не является целым числом
    """
    @wraps(func)
    def wrapper(left: float, right: float) -> float:
        if not right.is_integer() or not left.is_integer():
            raise OperationError(left, "", right, "операция допустима только над целыми числами")
        return func(left, right)
    return wrapper


_OP_MAP = {
    "+": BinaryOperator("+", ops.add),
    "-": BinaryOperator("-", ops.sub),
    "*": BinaryOperator("*", ops.mul),
    "/": BinaryOperator("/", assert_right_is_non_zero(ops.truediv)),
    "#": BinaryOperator("//", assert_right_is_non_zero(assert_integers(ops.floordiv))),
    "%": BinaryOperator("%", assert_right_is_non_zero(assert_integers(ops.mod))),
    "^": BinaryOperator("**", ops.pow),
}
"""
Flyweight объекты операторов
"""
