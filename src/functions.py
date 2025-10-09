from typing import Iterator, Callable

from src.common import remove_extra_brackets


class FunctionSyntaxError(Exception):
    pass


class FunctionExecutionError(Exception):
    pass


class Function:
    """
    Обертка над мат. функциями
    """

    __callable: Callable[..., float]

    def __init__(self, _callable: Callable[..., float]):
        self.__callable = _callable

    @classmethod
    def try_parse_function_call(cls, expression: str) -> tuple[str | None, tuple[str, ...] | None]:
        """
        Извлекает название функции и список строковых аргументов из строки вида 'func(a,b,...)'
        Аргументы возвращаются строками, а не вычисленными выражениями по двум причинам:
        1) чтобы избежать рекурсивных зависимостей (функции уже вызываются из выражений)
        2) чтобы переиспользовать методы при объявлении польз. функций (там в качестве аргументов будут идентификаторы)
        :param expression: Строка формата <func_name>(<arg>[,<arg>]*)
        :return: (название функции, список строковых аргументов)
        """
        first_open_bracket = expression.find("(")
        if first_open_bracket == -1:
            return None, None

        identifier = expression[:first_open_bracket]
        args_string = cls.__grab_to_closing_bracket(expression, first_open_bracket)
        args_string = remove_extra_brackets(args_string)
        args = tuple(cls.__parse_args(args_string))

        return identifier, args

    @staticmethod
    def __grab_to_closing_bracket(expression: str, open_bracket_pos: int) -> str:
        """
         Возвращает часть строки от открывающей скобки, до парной ей закрывающей (включая сами скобки).
        :param expression: Произвольное строковое выражение
        :param open_bracket_pos: Индекс открывающей скобки в строке
        :return: Часть строки от открывающей скобки, до парной ей закрывающей (включая сами скобки)
        :raises FunctionSyntaxError: Неверная конфигурация скобок
        """
        if expression[open_bracket_pos] != "(":
            raise FunctionSyntaxError("Неверная позиция открывающей скобки")

        brackets_counter = 0
        for i, sym in enumerate(expression[open_bracket_pos:]):
            if sym == "(":
                brackets_counter += 1
            elif sym == ")":
                brackets_counter -= 1

            if brackets_counter < 0:
                raise FunctionSyntaxError("Нарушен баланс скобок")

            if brackets_counter == 0:
                # проверяем, что скобка закрылась в конце выражения
                # исключает случаи вроде max(1,2)abc
                if open_bracket_pos+i+1 != len(expression):
                    raise FunctionSyntaxError("Ошибка в синтаксисе вызова функции")

                return expression[open_bracket_pos:open_bracket_pos+i+1]

        raise FunctionSyntaxError("Отсутствует закрывающая скобка")

    @staticmethod
    def __parse_args(args_string: str) -> Iterator[str]:
        """
        Выделяет из строки аргументы, разделенные запятой.
        Отличие от split: учитывает скобки. Разделение происходит только на верхнем уровне.
        Позволяет использовать вызов другой функции как аргумент.
        :param args_string: Строка без внешних скобок, где аргументы разделены запятыми
        :raises FunctionSyntaxError: Нарушен синтаксис аргументов
        :return: Поочередно возвращает каждый аргумент в виде строки
        """
        brackets = 0
        start_index = 0
        for ind, sym in enumerate(args_string):
            if sym == "(":
                brackets += 1
            elif sym == ")":
                brackets -= 1

            if brackets < 0:
                raise FunctionSyntaxError("Нарушен баланс скобок")

            if sym == "," and brackets == 0:
                arg = args_string[start_index:ind]

                if not arg:
                    raise FunctionSyntaxError("Нарушен синтаксис аргументов")

                yield arg
                start_index = ind + 1

        arg = args_string[start_index:]
        if not arg:
            raise FunctionSyntaxError("Нарушен синтаксис аргументов")

        yield arg

    def __call__(self, *args) -> float:
        """
        Вызывает непосредственно мат. функцию и возвращает результат.
        :param args: Числовые аргументы, которые будут переданы функции
        :return: Результат выполнения функции приведенный к float
        """
        try:
            return float(self.__callable(*args))
        except TypeError as e:
            if "argument" in str(e):
                raise FunctionSyntaxError(f"Неверные аргументы функции: {str(e)}")
            raise FunctionExecutionError(str(e)) from e
        except Exception as e:
            raise FunctionExecutionError(str(e)) from e
