import unittest

from src.functions import Function, FunctionSyntaxError


class TestParseFunctionCall(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(("func", ("1.5", )), Function.try_parse_function_call("func(1.5)"))

    def test_multiple_args(self):
        self.assertEqual(("max", ("2.5", "3", "8")), Function.try_parse_function_call("max(2.5,3,8)"))

    def test_expression_as_arg(self):
        self.assertEqual(("min", ("2.5*2/(3+5)", "5^(2-(1/2))+6")),
                         Function.try_parse_function_call("min(2.5*2/(3+5),5^(2-(1/2))+6)"))

    def test_function_call_as_arg(self):
        self.assertEqual(("func_name", ("2.5*max(3.5,min(10,8),abs(-15))", "sqrt(pow(25/5,2))")),
                         Function.try_parse_function_call("func_name(2.5*max(3.5,min(10,8),abs(-15)),sqrt(pow(25/5,2)))"))

    def test_broken_brackets_0(self):
        with self.assertRaises(FunctionSyntaxError):
            Function.try_parse_function_call("func(0")

    def test_broken_brackets_1(self):
        self.assertEqual((None, None), Function.try_parse_function_call("func0)"))

    def test_broken_brackets_2(self):
        with self.assertRaises(FunctionSyntaxError):
            Function.try_parse_function_call("func(max(1,2)")

    def test_broken_brackets_3(self):
        with self.assertRaises(FunctionSyntaxError):
            Function.try_parse_function_call("func(1, 2, 3)abc")

if __name__ == '__main__':
    unittest.main()
