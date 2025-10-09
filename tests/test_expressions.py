import unittest
from typing import Iterable

from src.expressions import Expression as Ex, ExpressionSyntaxError, TokenizedExpression
from src.common import remove_extra_brackets
from src.operators import BinaryOperator


bop = BinaryOperator.from_symbol
"""
Шорткат для BinaryOperator.from_symbol
"""


class TestRemoveExtraBrackets(unittest.TestCase):
    """
    Тестирует внутреннюю функцию remove_extra_brackets, убирающую лишние скобки из выражения (внешние)
    """

    def __assert_equal(self, arg: str, result: str):
        """
        Простой шорткат для проверки вход -> выход
        :param arg: Аргумент, который будет передан remove_extra_brackets
        :param result: Ожидаемый результат remove_extra_brackets
        """
        self.assertEqual(result, remove_extra_brackets(arg))    # type: ignore

    def test_basic(self):
        self.__assert_equal("(1 + 2)", "1 + 2")

    def test_no_extra(self):
        self.__assert_equal("4*2+3/2", "4*2+3/2")

    def test_multiple_extra(self):
        self.__assert_equal("((2*3+5))", "2*3+5")

    def test_fake_extra(self):
        self.__assert_equal("(-1)*(2+5*(3+1))/(2+1)", "(-1)*(2+5*(3+1))/(2+1)")

    def test_real_and_fake_extra(self):
        self.__assert_equal("((-3*2)+(2+(3/2)*2))", "(-3*2)+(2+(3/2)*2)")

    def test_wrong_brackets_configuration_0(self):
        self.__assert_equal("(-2))", "(-2))")

    def test_wrong_brackets_configuration_1(self):
        self.__assert_equal("((-5*4+3)", "((-5*4+3)")

    def test_wrong_brackets_configuration_2(self):
        self.__assert_equal("(((-5)(*4+3))", "(((-5)(*4+3))")


class TestSplitByOperators(unittest.TestCase):

    def __assert_equal(self, arg: str, ops: Iterable[str], result: TokenizedExpression | None):
        self.assertEqual(result, Ex._Expression__split_by_operators(arg, *ops))    # type: ignore

    def __assert_raises(self, arg: str, ops: Iterable[str], raises: type[Exception]):
        with self.assertRaises(raises):
            Ex._Expression__split_by_operators(arg, *ops)    # type: ignore

    def test_basic(self):
        self.__assert_equal("1+2", "+-", [Ex("1"), bop("+"), Ex("2")])

    def test_multiple(self):
        self.__assert_equal("1+2-3.2", "+-", [Ex("1"), bop("+"), Ex("2"), bop("-"), Ex("3.2")])

    def test_not_matching_ops(self):
        self.__assert_equal("1*2.456+3/4-5%6", "+-", [Ex("1*2.456"), bop("+"), Ex("3/4"), bop("-"), Ex("5%6")])

    def test_brackets(self):
        self.__assert_equal("1+(2-3.04)+4", "+-", [Ex("1"), bop("+"), Ex("(2-3.04)"), bop("+"), Ex("4")])

    def test_alpha(self):
        self.__assert_equal("1*a/bcd(3,4.1)*6", "*/", [Ex("1"), bop("*"), Ex("a"), bop("/"), Ex("bcd(3,4.1)"), bop("*"), Ex("6")])

    def test_no_split(self):
        self.__assert_equal("1*2/3.08%(4-(2+1)-(2*3))^8", "+-", None)

    def test_unknown_operator(self):
        self.__assert_raises("1&2.0", "+-&", ExpressionSyntaxError)

    def test_repeated_op(self):
        self.__assert_raises("1+-2-2.3", "+-", ExpressionSyntaxError)

    def test_empty_input(self):
        self.__assert_raises("", "+-", ExpressionSyntaxError)

    def test_not_closed_brackets(self):
        self.__assert_raises("1+2*(3+(5)-1", "+-", ExpressionSyntaxError)

    def test_not_opened_brackets(self):
        self.__assert_raises("1*(2^3)/4)^3", "*/", ExpressionSyntaxError)


class TestExecuteBinaryOperators(unittest.TestCase):

    def __assert_equal(self, arg: TokenizedExpression, result: float, reversed_execution_order: bool = False):
        """
        Шорткат для проверки __execute_bin_ops(arg, reversed_execution_order) == result через assertEqual
        """
        self.assertEqual(result, Ex._Expression__execute_bin_ops(arg, reversed_execution_order))    # type: ignore

    def test_single(self):
        self.__assert_equal([Ex("1.5"), bop("+"), Ex("2.3")], 3.8)

    def test_multiple(self):
        self.__assert_equal([Ex("4"), bop("*"), Ex("0.5"), bop("/"), Ex("2"), bop("%"), Ex("3")], 1)

    def test_recursive(self):
        self.__assert_equal([Ex("(2+2.5)"), bop("*"), Ex("(5#3+1)")], 9)

    def test_right_associative(self):
        self.__assert_equal([Ex("2"), bop("^"), Ex("3"), bop("^"), Ex("2")], 512, True)


if __name__ == '__main__':
    unittest.main()
