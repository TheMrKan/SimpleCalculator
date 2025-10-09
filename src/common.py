from typing import TypeAlias, Union, TYPE_CHECKING
import string

if TYPE_CHECKING:
    from src.functions import Function


class UserFriendlyException(Exception):
    pass


class InvalidIdentifierError(Exception):
    pass


Nametable: TypeAlias = dict[str, Union[float, "Function"]]

IDENTIFIER_ALLOWED_CHARACTERS = set(string.ascii_lowercase + string.digits + "_")
"""
Символы, разрешенные для использования в идентификаторах
"""


def remove_extra_brackets(expression: str) -> str:
    """
    Убирает все лишние (внешние) парные скобки из выражения.
    Пример: (((-1) * 2 + 3 + (5 - 6))) -> (-1) * 2 + 3 + (5 - 6)
    :param expression: Строка с мат. выражением
    :return:
        Входная строка, но без внешних скобок. Если баланс скобок не соблюден, то возвращает
        исходное выражение без изменений
    """
    while True:  # цикл, т. к. может быть несколько пар скобок
        if not expression.startswith("(") or not expression.endswith(")"):
            return expression

        brackets = 0  # счетчик баланса скобок
        for index, sym in enumerate(expression):
            if sym == "(":
                brackets += 1
            elif sym == ")":
                brackets -= 1

            # лишняя закрывающая скобка
            if brackets < 0:
                return expression

            # проверяем, где закрылась первая открывающая скобка
            if brackets == 0:
                # если на конце, значит их можно убрать
                if index == len(expression) - 1:
                    expression = expression[1:-1]
                    break
                # иначе скобка закрывается внутри выражения
                # более внешних скобок быть не может
                else:
                    return expression

        # недостаточно открывающих скобок
        if brackets > 0:
            return expression
