import unittest
from unittest import TestCase

from src.calculator import Calculator
from src.common import UserFriendlyException


class TestCalculatorCorrect(TestCase):

    calc: Calculator

    def setUp(self):
        self.calc = Calculator()

    def test_basic_ops(self):
        self.assertEqual(-17.8, self.calc.execute("5.2 - 2*3/0.5**2 + 7%4//2"))

    def test_brackets(self):
        self.assertEqual(7.5, self.calc.execute("5 + (-1)*((2+3/(2-1)))/(2-4)"))

    def test_unary(self):
        self.assertEqual(4, self.calc.execute("-1 + (+2*3) - (-(+(-1)))"))

    def test_very_long(self):
        self.assertEqual(-40, self.calc.execute('-'.join(["5 + (-1)*((2+3/(2-1)))/(2-4)" for _ in range(20)])))


class TestCalculatorInvalidSyntax(TestCase):

    calc: Calculator

    def setUp(self):
        self.calc = Calculator()

    def test_empty(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('    \n   ')

    def test_wrong_ops_0(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('-')

    def test_wrong_ops_1(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('1-+2')

    def test_missing_ops_0(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('1(2+3)')

    def test_missing_ops_1(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('(2+3)(3/4)')

    def test_wrong_unary(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('1+(*2)')

    def test_wrong_brackets_0(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('5 + (1')

    def test_wrong_brackets_1(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('5 + 1)')

    def test_wrong_brackets_2(self):
        with self.assertRaises(UserFriendlyException):
            self.calc.execute('(5 + ((1))))')


if __name__ == '__main__':
    unittest.main()
