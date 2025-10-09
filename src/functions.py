from typing import Iterator, Callable, Self

from src.common import remove_extra_brackets, InvalidIdentifierError, IDENTIFIER_ALLOWED_CHARACTERS


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

    def __call__(self, *args, **kwargs) -> float:
        """
        Вызывает непосредственно мат. функцию и возвращает результат.
        **kwargs используется для передачи служебной информации и не передается в саму функцию
        **kwargs не используется в этой реализации, но может использоваться в других (например UserDefinedFunction)
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


class UserDefinedFunction(Function):

    @classmethod
    def is_function_definition(cls, string: str) -> bool:
        """
        Проверяет, содержит ли строка определение функции.
        :return: True, если в строке содержится определение функции; иначе False
        """
        return string.startswith("lambda")

    @classmethod
    def build_from_string(cls, string: str) -> Self:
        """
        Собирает мат. функцию (аналог lambda из Python) из строки вида "lambda(x,y,z):x+y+z"
        :param string: Строка вида "lambda(x,y,z):x+y+z"
        :return: Экземпляр UserDefinedFunction, при вызове которого вычисляется указанное выражение с заданными переменными
        """

        if not string.startswith("lambda"):
            raise FunctionSyntaxError("Определение функции должно начинаться с 'lambda'")

        string = string[6:]    # убирает 'lambda' в начале
        try:
            args_string, expression = string.split(":")
        except ValueError:
            raise FunctionSyntaxError("Неверный синтаксис определения функции")

        args_string = args_string.strip("()")    # убирает скобки, оставляя только аргументы через запятую
        args = args_string.split(",")    # в аргументах не может быть скобок и выражений, поэтому просто делим по запятой
        for arg in args:
            cls.__assert_arg_name_is_valid(arg)

        # ---------------- WIP ----------------
        raise NotImplementedError

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
