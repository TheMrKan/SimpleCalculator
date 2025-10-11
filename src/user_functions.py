from typing import Callable, Iterable, Sequence

from src.functions import Function, FunctionSyntaxError, FunctionExecutionError
from src.common import InvalidIdentifierError, IDENTIFIER_ALLOWED_CHARACTERS, Nametable
from src.expressions import Expression


class UserFunctionDefiner:

    @classmethod
    def is_function_definition(cls, string: str) -> bool:
        """
        Проверяет, содержит ли строка определение функции.
        :return: True, если в строке содержится определение функции; иначе False
        """
        return string.startswith("lambda")

    @classmethod
    def build_function_from_string(cls, string: str) -> Function:
        """
        Собирает мат. функцию (аналог lambda из Python) из строки вида "lambda(x,y,z):x+y+z"
        :param string: Строка вида "lambda(x,y,z):x+y+z"
        :return: Экземпляр UserDefinedFunction, при вызове которого вычисляется указанное выражение с заданными переменными
        """

        if not string.startswith("lambda"):
            raise FunctionSyntaxError("Определение функции должно начинаться с 'lambda'")

        string = string[6:]    # убирает 'lambda' в начале
        try:
            args_string, expression_string = string.split(":")
        except ValueError:
            raise FunctionSyntaxError("Неверный синтаксис определения функции")

        args_string = args_string.strip("()")     # убирает скобки, оставляя только аргументы через запятую
        args = args_string.split(",")    # в аргументах не может быть скобок и выражений, поэтому просто делим по запятой
        for arg in args:
            cls.__assert_arg_name_is_valid(arg)

        expression = Expression(expression_string)

        return UserDefinedFunction(expression.evaluate, args)

    @classmethod
    def __assert_arg_name_is_valid(cls, arg_name: str):
        """
        Проверяет, что строка может являться названием аргумента функции.
        :raises InvalidIdentifierError: Строка не может являться названием аргумента функции.
        """
        if not arg_name:
            raise InvalidIdentifierError("Недопустимое пустое название аргумента")

        if not arg_name[0].isalpha():
            raise InvalidIdentifierError("Название аргумента должно начинаться с буквы")

        for sym in arg_name:
            if sym not in IDENTIFIER_ALLOWED_CHARACTERS:
                raise InvalidIdentifierError(f"Символ '{sym}' не может использоваться в имени аргумента")


class UserDefinedFunction(Function):
    """
    Мат. функция, заданная пользовательскм выражением через lambda
    """

    arg_names: Sequence[str]
    _callable: Callable[[Nametable, ], float]

    def __init__(self, _callable: Callable[[Nametable, ], float], arg_names: Sequence[str]):
        self.arg_names = arg_names
        self._callable = _callable

    def __call__(self, *args: float, name_table: Nametable | None = None, **kwargs) -> float:
        """
        Вычисляет выражение, заданное пользователем, с учетом аргументов.
        :param args: Числовые аргументы, которые будут переданы функции
        :return: Результат выполнения функции приведенный к float
        """

        try:
            if name_table is not None:
                name_table = name_table.copy()    # чтобы не изменять исходную таблицу
            else:
                name_table = Nametable()
            self.__extend_nametable(name_table, args, self.arg_names)

            return self._callable(name_table)
        except RecursionError:
            raise
        except (FunctionSyntaxError, FunctionExecutionError):
            raise
        except Exception as e:
            raise FunctionExecutionError(str(e)) from e

    @classmethod
    def __extend_nametable(cls, name_table: Nametable, args: Iterable[float], arg_names: Sequence[str]):
        """
        Преобразует позиционные аргументы из 'args' в именованные через сопоставление с 'arg_names' и добавляет их в таблицу.
        Используется для создания локальных таблиц при вызове функций.
        :param name_table: Таблица имен, в которую будут добавлены аргументы.
        :param args: Позиционные аргументы, переданные функции.
        :param arg_names: Сигнатура аргументов функции/
        :return: Ничего не возвращает, т. к. изменяет 'name_table'
        """
        index = 0
        for index, value in enumerate(args):
            if index >= len(arg_names):
                raise FunctionSyntaxError("Переданы лишние аргументы")

            name_table[arg_names[index]] = value

        if index < len(arg_names) - 1:
            raise FunctionSyntaxError("Недостаточно параметров для вызова функции")
