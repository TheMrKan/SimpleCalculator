from src.calculator import Calculator
from src.common import UserFriendlyException


def main() -> None:
    """
    CLI. В бесконечном цикле принимает ввод из stdin, выполняет его в Calculator, выводит результаты и возникающие исключения в stdout.
    """

    calculator = Calculator()

    while True:
        try:
            user_input = input(">>> ")

            result = calculator.execute(user_input)

            if result is None:    # например, присвоение переменной
                print("OK")
            else:
                print(result)
        except UserFriendlyException as e:
            print(e)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {type(e).__name__}('{str(e)}')")


if __name__ == "__main__":
    main()
