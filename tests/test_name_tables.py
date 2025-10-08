import unittest

from src.common import InvalidIdentifierError
from src.name_tables import NametableManager


class TestIsDeclaration(unittest.TestCase):

    def test_basic_positive(self):
        self.assertTrue(NametableManager.is_declaration('x=2'))

    def test_basic_negative(self):
        self.assertFalse(NametableManager.is_declaration('1+2'))


class TestVarDeclaration(unittest.TestCase):

    nt_manager: NametableManager

    def setUp(self):
        self.nt_manager = NametableManager()

    def test_basic(self):
        self.nt_manager.declare_from_string("x=2")
        self.assertEqual({"x": 2.0}, self.nt_manager.name_table)

    def test_expression(self):
        self.nt_manager.declare_from_string("x=2+2*2")
        self.assertEqual({"x": 6.0}, self.nt_manager.name_table)

    def test_multiple(self):
        self.nt_manager.declare_from_string("x=3")
        self.nt_manager.declare_from_string("y=4")
        self.assertEqual({"x": 3.0, "y": 4.0}, self.nt_manager.name_table)

    def test_redeclaration(self):
        self.nt_manager.declare_from_string("x=3")
        self.nt_manager.declare_from_string("x=4")
        self.assertEqual({"x": 4.0}, self.nt_manager.name_table)

    def test_recursive(self):
        self.nt_manager.declare_from_string("x=5")
        self.nt_manager.declare_from_string("x=2*x+1/x")
        self.assertEqual({"x": 10.2}, self.nt_manager.name_table)

    def test_invalid_identifier(self):
        with self.assertRaises(InvalidIdentifierError):
            self.nt_manager.declare_from_string("123=5")

    def test_multiple_eq_ops(self):
        with self.assertRaises(SyntaxError):
            self.nt_manager.declare_from_string("x=5=7")


if __name__ == '__main__':
    unittest.main()
