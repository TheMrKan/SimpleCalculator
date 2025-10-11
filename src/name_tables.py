import math

from src.common import InvalidIdentifierError, Nametable, IDENTIFIER_ALLOWED_CHARACTERS
from src.expressions import Expression
from src.functions import Function, CodeBasedFunction
from src.user_functions import UserFunctionDefiner


class NametableManager:

    name_table: Nametable

    def __init__(self):
        self.name_table = BUILTINS.copy()

    @staticmethod
    def is_declaration(user_input: str) -> bool:
        """
        Проверяет, является ли ввод объявлением переменной.
        :return: True, если в переданной строке объявляется переменная; иначе False.
        """
        return "=" in user_input

    def declare_from_string(self, user_input: str):
        """
        Объявляет переменную из строки вида "id=12+5". Объявленная переменная добавится в name_table с вычисленным значением {"id": 17}.
        Использует Expression.evaluate для вычисления выражения.
        :param user_input: Строка, содержащая '='. Слева от '=' - идентификатор, справа - выражение.
        :raises SyntaxError: Неверный синтаксис объявления
        :raises InvalidIdentifier: Неверный идентификатор
        :raises исключения из Expression.evaluate: Ошибка при вычислении значения выражения
        """
        try:
            identifier, value_string = user_input.split("=")
        except ValueError:
            raise SyntaxError("Неверный синтаксис объявления")

        self.__assert_identifier_valid(identifier)

        value: float | Function
        if UserFunctionDefiner.is_function_definition(value_string):
            value = UserFunctionDefiner.build_function_from_string(value_string)
        else:
            value = Expression(value_string).evaluate(name_table=self.name_table)

        self.name_table[identifier] = value

    @staticmethod
    def __assert_identifier_valid(identifier: str) -> None:
        """
        Проверяет, что строка может являться идентификатором.
        :raises InvalidIdentifierError: Строка не может являться идентификатором.
        """
        if not identifier:
            raise InvalidIdentifierError("Пустой идентификатор")

        if not identifier[0].isalpha():
            raise InvalidIdentifierError("Идентификатор должен начинаться с буквы")

        for char in identifier.lower():
            if char not in IDENTIFIER_ALLOWED_CHARACTERS:
                raise InvalidIdentifierError(f"Символ '{char}' не может использоваться в идентификаторе")


BUILTINS = {
    "max": CodeBasedFunction(max),
    "min": CodeBasedFunction(min),
    "abs": CodeBasedFunction(abs),    # type: ignore
    "sqrt": CodeBasedFunction(math.sqrt),    # type: ignore
    "pow": CodeBasedFunction(math.pow),
}
