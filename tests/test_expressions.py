import unittest

from src.expressions import Expression


class TestExtraBracketsRemoval(unittest.TestCase):
    """
    Тестирует внутреннюю функцию __remove_extra_brackets, убирающую лишние скобки из выражения (внешние)
    """

    def __assert_equal(self, arg: str, result: str):
        """
        Простой шорткат для проверки вход -> выход
        :param arg: Аргумент, который будет передан __remove_extra_brackets
        :param result: Ожидаемый результат __remove_extra_brackets
        """
        self.assertEqual(Expression._Expression__remove_extra_brackets(arg), result)    # type: ignore

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


if __name__ == '__main__':
    unittest.main()
