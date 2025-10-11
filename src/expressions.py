from typing import TypeAlias, ForwardRef, Any

from src.operators import BinaryOperator, OperationError
from src.common import UserFriendlyException, InvalidIdentifierError, Nametable, remove_extra_brackets
from src.functions import Function, FunctionSyntaxError, FunctionExecutionError


TokenizedExpression: TypeAlias = list[ForwardRef('Expression') | BinaryOperator]    # type: ignore


class ExpressionSyntaxError(Exception):
    pass


class Expression:
    """
    Объект вычисляемого мат. выражения
    """

    expression: str | float

    def __init__(self, expression: str | float):
        self.expression = expression

    def evaluate(self, name_table: Nametable | None = None) -> float:
        """
        Рекурсивным спуском вычисляет значение мат. выражения.
        :param name_table: Таблица имен, через которую в выражении могут быть задействованы переменные и функции.
        :return: Значение выражения, приведенное к float
        """
        if isinstance(self.expression, (float, int)):
            return self.expression

        prepared = remove_extra_brackets(self.expression)

        try:
            no_leading_zeros = prepared.lstrip("0_")    # lstrip убирает ведущие нули и _
            if prepared and not no_leading_zeros:    # на случай, если значение 0
                return 0
            return float(no_leading_zeros)
        except ValueError:
            pass

        prepared = self.__add_zero_if_needed(prepared)

        try:
            tokenized, reversed_execution_order = self.__try_tokenize(prepared)
            if not tokenized:
                return self.__interpret_as_identifier(prepared, name_table or {})
        except (ExpressionSyntaxError, InvalidIdentifierError) as e:
            raise UserFriendlyException(f"Ошибка в выражении: {self.expression}\n{str(e)}") from e
        except (FunctionSyntaxError, FunctionExecutionError) as e:
            raise UserFriendlyException(f"Ошибка в вызове функции: {self.expression}\n{str(e)}") from e
        except RecursionError:
            raise

        try:
            return self.__execute_bin_ops(tokenized, reversed_execution_order, name_table)    # type: ignore
        except ExpressionSyntaxError as e:
            raise UserFriendlyException(f"Ошибка вычисления выражения: {self.expression}\n{str(e)}") from e
        except OperationError as e:
            raise UserFriendlyException(f"Ошибка вычисления выражения: {self.expression}\n{str(e)}") from e

    def __try_tokenize(self, expression: str) -> tuple[TokenizedExpression | None, bool | None]:
        """
        Пытается разделить выражение по операторам одного приоритета.
        :param expression: Строковое мат. выражение
        :return:
            (список выражений и операторов (см. __split_by_operators), порядок выполнения операторов)
            Если порядок - False, то операторы применяются слева-направо, иначе справа-налево.
            Т. е. True означает, что разбиение произошло по правоассоциативным операторам
            Возвращает (None, None), если не удалось сделать ни одного разделения.
        """
        if tokenized := self.__split_by_operators(expression, "+", "-"):
            return tokenized, False
        if tokenized := self.__split_by_operators(expression, "*", "/", "#", "%"):
            return tokenized, False
        if tokenized := self.__split_by_operators(expression, "^"):
            return tokenized, True

        return None, None

    @staticmethod
    def __interpret_as_identifier(expression: str, name_table: Nametable) -> float | Any:
        """
        Пытается интерпретировать выражение как идентификатор (название переменной/функции).
        Если идентификатор принадлежит переменной, то возвращает её значение.
        Если идентификатор принадлежит функции, то вызывает её с аргументами и возвращает результат.
        :param expression: Строковое выражение, содержащее название переменной или вызов функции.
        :raises InvalidIdentifierError: Идентификатор не найден или используется
        :return: Значение переменной или результат выполнения функции
        """

        identifier, args = Function.try_parse_function_call(expression)
        if identifier is None:
            identifier = expression

        try:
            identifier_target = name_table[identifier]
        except KeyError:
            raise InvalidIdentifierError(f"Неизвестный идентификатор: {identifier}")

        if args is not None:    # вызываем функцию
            if not isinstance(identifier_target, Function):
                raise InvalidIdentifierError(f"'{identifier}' не является функцией")

            evaluated_args = (Expression(arg).evaluate(name_table=name_table) for arg in args)
            return identifier_target(*evaluated_args, name_table=name_table)

        else:    # возвращаем значение переменной
            if not isinstance(identifier_target, (float, int)):
                raise InvalidIdentifierError(f"'{identifier}' не может использоваться как переменная")

            return identifier_target

    @staticmethod
    def __add_zero_if_needed(expression: str) -> str:
        """
        Если выражение начинается с унарного минуса/плюса, то добавляет 0 в начало, преобразуя минус/плюс в бинарный
        для упрощения дальнейшей обработки.

        Пример: -2+5 -> 0-2+5 ; +3*2 -> 0+3*2 ; 2*5 -> 2*5
        :param expression: Строка с мат. выражением
        :return: Входная строка с 0 в начале, если он необходим; иначе исходная строка без изменений
        """
        if expression[0] in "+-":
            return "0" + expression
        return expression

    @staticmethod
    def __validate_expression_start(edge_char: str) -> bool:
        """
        Проверяет, может ли мат. выражение начинаться с указанного символа.
        Если возвращает False, то мат. выражение считается некорректным
        :param edge_char: Первый символ мат. выражения
        :return: True, если может; иначе False
        """
        # проверка .isalnum() нужна для поддержки функций и переменных
        # +- включен для унарных
        # . для поддержки float как в python: .5
        return edge_char in "-+()." or edge_char.isalnum()

    @staticmethod
    def __validate_expression_end(edge_char: str) -> bool:
        """
        Проверяет, может ли мат. выражение заканчиваться на указанный символ.
        Если возвращает False, то мат. выражение считается некорректным
        :param edge_char: Последний символ мат. выражения
        :return: True, если может; иначе False
        """
        # проверка .isalnum() нужна для поддержки функций и переменных
        return edge_char in "()" or edge_char.isalnum()

    @classmethod
    def __split_by_operators(cls, expression: str, *operators: str) -> TokenizedExpression | None:
        """
        Разделяет выражение на список с чередованием 'выражение-оператор-выражение'
        [Expression, (Operator, Expression)+] с учетом скобок.
        Разделение происходит только на верхнем уровне, т. е. внутри скобок разделение не будет выполнено.
        Предполагается, что разделение выполняется по максимально приоритетным на данном этапе операторам.
        Считается, что переданные операторы имеют равный приоритет.
        :param expression: Строка с исходным мат. выражением
        :param operators:
            Символы, которые могут являться операторами при разделении.
            Один аргумент = один символ = один оператор
        :raises ExpressionSyntaxError: Ошибка в выражении: нарушен баланс скобок, неизвестный оператор, либо содержится недопустимое выражение
        :return:
            Список выражений и операторов, если удалось сделать хотя бы одно разделение;
            иначе None, если ни одна операция не должна быть выполнена
        """
        if not any(operators):
            raise ValueError("Должен быть передан хотя бы один оператор")

        result: TokenizedExpression = []
        current_part: list[str] = []
        brackets = 0
        for i in range(len(expression)):
            sym = expression[i]

            if sym == "(":
                brackets += 1
            elif sym == ")":
                brackets -= 1

            if brackets < 0:
                raise ExpressionSyntaxError("Лишние закрывающие скобки")

            # проверка brackets == 0, чтобы избежать разделения внутри скобок
            if brackets == 0 and sym in operators:
                joined = "".join(current_part)

                if (not joined or not cls.__validate_expression_start(joined[0])
                        or not cls.__validate_expression_end(joined[-1])):
                    raise ExpressionSyntaxError(f"Недопустимое выражение: '{joined}'")

                current_part.clear()
                result.append(Expression(joined))
                try:
                    result.append(BinaryOperator.from_symbol(sym))
                except KeyError:
                    raise ExpressionSyntaxError(f"Неизвестный оператор: '{sym}'")
                continue

            current_part.append(sym)

        # случай <0 обрабатывается в цикле
        # теоретически здесь должен оказываться только случай >0, т. е. недостаток закрывающих скобок
        # однако для надежности проверяются оба случая
        if brackets != 0:
            raise ExpressionSyntaxError("Имеются незакрытые скобки")

        # обработка последнего куска выражения
        # необходимо, т. к. в цикле добавление происходит при нахождении оператора, которого в конце нет
        joined = "".join(current_part)
        if not joined or not cls.__validate_expression_start(joined[0]) or not cls.__validate_expression_end(joined[-1]):
            raise ExpressionSyntaxError(f"Недопустимое выражение: '{joined}'")
        result.append(Expression(joined))

        # если длина 1, значит разделения не было - возвращаем None
        if len(result) > 1:
            return result

        return None

    @classmethod
    def __execute_bin_ops(cls, tokenized: TokenizedExpression, reversed_execution_order: bool = False, name_table: Nametable | None = None) -> float:
        """
        Поочередно (слева направо или справа налево) применяет бинарные операторы на выражениях. Не изменяет исходное выражение.
        В конце выполнения в стэке должно остаться одно число, которое будет возвращено функцией.
        :param tokenized: Список токенов с чередованием 'выражение-оператор-выражение'
        :param reversed_execution_order: False - операторы применяются слева направо. True - справа налево. (для правоассоциативных операторов)
        :return: Числовое значение, получившееся после применения всех операторов
        :raises ExpressionSyntaxError: Неверный порядок токенов в выражении
        """
        stack: TokenizedExpression = []

        if reversed_execution_order:
            tokenized = reversed(tokenized)

        for token in tokenized:
            stack.append(token)

            if len(stack) < 3:
                continue

            left, op, right = stack.pop(0), stack.pop(0), stack.pop(0)
            if reversed_execution_order:
                left, right = right, left

            if not isinstance(left, Expression):
                raise ExpressionSyntaxError(f"'{left}' должен быть выражением")

            if not isinstance(op, BinaryOperator):
                raise ExpressionSyntaxError(f"'{op}' должен быть оператором")

            if not isinstance(right, Expression):
                raise ExpressionSyntaxError(f"'{right}' должен быть выражением")

            val = op(left.evaluate(name_table=name_table), right.evaluate(name_table=name_table))
            stack.insert(0, Expression(val))

        if len(stack) != 1:
            raise ExpressionSyntaxError("Неверный набор выражений")

        assert isinstance(stack[0], Expression)

        return stack[0].evaluate()

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Expression):
            raise NotImplementedError(f"Compression between Expression and {type(other).__name__} is not implemented")

        return self.expression == other.expression
