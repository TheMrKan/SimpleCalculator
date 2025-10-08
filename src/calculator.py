from src.expressions import Expression
from src.common import UserFriendlyException
from src.name_tables import NametableManager


class Calculator:

    nt_manager: NametableManager

    def __init__(self):
        self.nt_manager = NametableManager()

    def execute(self, user_input: str) -> float | None:
        prepared = self.__clean(user_input)
        prepared = self.__translate_operators(prepared)

        if not prepared:
            raise UserFriendlyException("Пустой ввод")

        if self.nt_manager.is_declaration(prepared):
            try:
                self.nt_manager.declare_from_string(prepared)
            except Exception as e:
                raise UserFriendlyException(f"Ошибка при объявлении переменной: {str(e)}") from e

            return None

        expression = Expression(prepared)
        return expression.evaluate(name_table=self.nt_manager.name_table)

    @staticmethod
    def __clean(user_input: str) -> str:
        return user_input.strip().replace(" ", "")

    @staticmethod
    def __translate_operators(user_input: str) -> str:
        return user_input \
                .replace("//", "#") \
                .replace("**", "^")
