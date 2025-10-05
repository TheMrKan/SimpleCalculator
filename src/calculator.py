from src.expressions import Expression


class Calculator:

    def execute(self, user_input: str) -> float | None:
        prepared = self.__clean(user_input)
        prepared = self.__translate_operators(prepared)

        expression = Expression(prepared)
        return expression.evaluate()

    @staticmethod
    def __clean(user_input: str) -> str:
        return user_input.replace(" ", "")

    @staticmethod
    def __translate_operators(user_input: str) -> str:
        return user_input \
                .replace("//", "#") \
                .replace("**", "^")
