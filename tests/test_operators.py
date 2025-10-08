from unittest import TestCase, main

from src.operators import BinaryOperator as Op, OperationError


class TestSimpleOperators(TestCase):

    def test_sum(self):
        self.assertEqual(11.5, Op.from_symbol("+")(13.6, -2.1))

    def test_sub(self):
        self.assertEqual(11.5, Op.from_symbol("-")(13.6, 2.1))

    def test_mul(self):
        self.assertEqual(9, Op.from_symbol("*")(6, 1.5))

    def test_pow(self):
        self.assertEqual(256, Op.from_symbol("^")(2, 8))


class TestTrueDiv(TestCase):

    def test_simple(self):
        self.assertEqual(1.5, Op.from_symbol("/")(6, 4))

    def test_zero_division(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("/")(6, 0)


class TestFloorDiv(TestCase):

    def test_simple(self):
        self.assertEqual(1, Op.from_symbol("#")(6, 4))

    def test_zero_division(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("#")(6, 0)

    def test_left_float(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("#")(6.5, 4)

    def test_right_float(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("#")(4, 6.5)


class TestModDiv(TestCase):

    def test_simple(self):
        self.assertEqual(1, Op.from_symbol("%")(6, 5))

    def test_zero_division(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("%")(6, 0)

    def test_left_float(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("%")(6.5, 4)

    def test_right_float(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("%")(4, 6.5)


class TestExtra(TestCase):

    def test_overflow(self):
        with self.assertRaises(OperationError):
            Op.from_symbol("^")(6, 1000)


if __name__ == '__main__':
    main()
