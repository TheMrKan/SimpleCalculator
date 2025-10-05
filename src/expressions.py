from typing import TypeAlias, ForwardRef

from src.operators import BinaryOperator, OperationError
from src.common import UserFriendlyException


TokenizedExpression: TypeAlias = list[ForwardRef('Expression') | BinaryOperator]


class Expression:

    expression: str | float

    def __init__(self, expression: str | float):
        self.expression = expression

    def evaluate(self) -> float:
        if isinstance(self.expression, float):
            return self.expression

        prepared = self.__remove_extra_brackets(self.expression)

        try:
            return float(prepared)
        except ValueError:
            pass

        prepared = self.__add_zero_if_needed(prepared)

        tokenized = self.__split_by_operators(prepared, "+", "-")
        if not tokenized:
            tokenized = self.__split_by_operators(prepared, "*", "/", "#", "%")
            if not tokenized:
                tokenized = self.__split_by_operators(prepared, "^")

        if not tokenized:
            raise ValueError(f"Не удалось прочитать выражение: {self.expression}")

        try:
            return self.__execute_bin_ops(tokenized)
        except OperationError as e:
            raise UserFriendlyException(f"Ошибка вычисления выражения: {self.expression}\n{str(e)}") from e

    @staticmethod
    def __remove_extra_brackets(expression: str) -> str:
        while True:
            if not expression.startswith("(") or not expression.endswith(")"):
                return expression

            brackets = 0
            for index, sym in enumerate(expression):
                if sym == "(":
                    brackets += 1
                elif sym == ")":
                    brackets -= 1

                if brackets < 0:
                    raise ValueError("Скобки не сбалансированы")

                if brackets == 0:
                    if index == len(expression) - 1:
                        expression = expression[1:-1]
                        break
                    else:
                        return expression

    @staticmethod
    def __add_zero_if_needed(expression: str) -> str:
        if expression[0] in "+-":
            return "0" + expression
        return expression

    @staticmethod
    def __validate_expression_start(edge_char: str) -> bool:
        return edge_char in "-+()" or edge_char.isalnum()

    @staticmethod
    def __validate_expression_end(edge_char: str) -> bool:
        return edge_char in "()" or edge_char.isalnum()

    @classmethod
    def __split_by_operators(cls, expression: str, *operators: str) -> TokenizedExpression | None:
        if not any(operators):
            raise ValueError("Нет операторов")

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
                raise ValueError("Много закрывающих")

            if brackets == 0 and sym in operators:
                joined = "".join(current_part)

                if (not joined or not cls.__validate_expression_start(joined[0])
                        or not cls.__validate_expression_end(joined[-1])):
                    raise ValueError(f"Некорректный ввод: {expression}")

                current_part.clear()
                result.append(Expression(joined))
                result.append(BinaryOperator.from_symbol(sym))
                continue

            current_part.append(sym)

        if brackets != 0:
            raise ValueError("Ошибка со скобками")

        joined = "".join(current_part)
        if not joined or not cls.__validate_expression_start(joined[0]) or not cls.__validate_expression_end(joined[-1]):
            raise ValueError(f"Некорректный ввод: {expression}")
        result.append(Expression(joined))

        if len(result) > 1:
            return result

        return None

    @classmethod
    def __execute_bin_ops(cls, tokenized: TokenizedExpression) -> float:
        stack: TokenizedExpression = []

        for token in tokenized:
            stack.append(token)

            if len(stack) < 3:
                continue

            left, op, right = stack.pop(0), stack.pop(0), stack.pop(0)

            if not isinstance(left, Expression):
                raise ValueError(f"{left} must be an expression")

            if not isinstance(op, BinaryOperator):
                raise ValueError(f"{op} must be an operator")

            if not isinstance(right, Expression):
                raise ValueError(f"{right} must be an expression")

            val = op(left.evaluate(), right.evaluate())
            stack.insert(0, Expression(val))

        if len(stack) != 1:
            raise ValueError("Недостаточно аргументов для бинарных операторов")

        assert isinstance(stack[0], Expression)

        return stack[0].evaluate()

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return str(self)
