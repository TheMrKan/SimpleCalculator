from typing import TypeAlias, ForwardRef, Any

from src.operators import BinaryOperator, OperationError
from src.common import UserFriendlyException


TokenizedExpression: TypeAlias = list[ForwardRef('Expression') | BinaryOperator]    # type: ignore


class ExpressionSyntaxError(Exception):
    pass


class Expression:

    expression: str | float

    def __init__(self, expression: str | float):
        self.expression = expression

    def evaluate(self) -> float:
        if isinstance(self.expression, (float, int)):
            return self.expression

        prepared = self.__remove_extra_brackets(self.expression)

        try:
            return float(prepared)
        except ValueError:
            pass

        prepared = self.__add_zero_if_needed(prepared)

        reversed_execution_order = False    # для правоассоциативных операторов
        try:
            tokenized = self.__split_by_operators(prepared, "+", "-")
            if not tokenized:
                tokenized = self.__split_by_operators(prepared, "*", "/", "#", "%")
                if not tokenized:
                    tokenized = self.__split_by_operators(prepared, "^")
                    reversed_execution_order = True
        except ExpressionSyntaxError as e:
            raise UserFriendlyException(f"Ошибка в выражении: {self.expression}\n{str(e)}") from e

        if not tokenized:
            raise UserFriendlyException(f"Неизвестное выражение: {self.expression}")

        try:
            return self.__execute_bin_ops(tokenized, reversed_execution_order)
        except ExpressionSyntaxError as e:
            raise UserFriendlyException(f"Ошибка вычисления выражения: {self.expression}\n{str(e)}") from e
        except OperationError as e:
            raise UserFriendlyException(f"Ошибка вычисления выражения: {self.expression}\n{str(e)}") from e

    @staticmethod
    def __remove_extra_brackets(expression: str) -> str:
        """
        Убирает все лишние (внешние) парные скобки из выражения.
        Пример: (((-1) * 2 + 3 + (5 - 6))) -> (-1) * 2 + 3 + (5 - 6)
        :param expression: Строка с мат. выражением
        :return:
            Входная строка, но без внешних скобок. Если баланс скобок не соблюден, то возвращает
            исходное выражение без изменений
        """
        while True:    # цикл, т. к. может быть несколько пар скобок
            if not expression.startswith("(") or not expression.endswith(")"):
                return expression

            brackets = 0    # счетчик баланса скобок
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
    def __execute_bin_ops(cls, tokenized: TokenizedExpression, reversed_execution_order: bool = False) -> float:
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

            val = op(left.evaluate(), right.evaluate())
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
