from src.expressions import Expression
from src.common import UserFriendlyException
from src.name_tables import NametableManager


class Calculator:
    """
    Калькулятор)
    Очищает пользовательский ввод, преобразует некоторые операторы.
    Управляет объявлением переменных, которые могут быть использованы в выражении.
    """

    nt_manager: NametableManager

    def __init__(self):
        self.nt_manager = NametableManager()

    def execute(self, user_input: str) -> float | None:
        """
        Обрабатывает пользовательский ввод.
        Вычисляет значение выражения или задает значение переменной в зависимости от ввода.
        :param user_input: Произвольная строка
        :return: Число, если значение вычислено; None, если было успешно выполнено действие (объявлена переменная)
        :raises UserFriendlyException: Ввод некорректен. Подробности в исключении.
        """
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
        try:
            return expression.evaluate(name_table=self.nt_manager.name_table)
        except RecursionError:
            raise UserFriendlyException("Достигнут лимит рекурсии")

    @staticmethod
    def __clean(user_input: str) -> str:
        """
        Убирает незначащие символы
        """
        return user_input.strip().replace(" ", "")

    @staticmethod
    def __translate_operators(user_input: str) -> str:
        """
        Преобразует операторы к виду, с которым работают внутренние функции
        """
        return user_input \
                .replace("//", "#") \
                .replace("**", "^")
