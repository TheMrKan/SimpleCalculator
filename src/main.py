from src.calculator import Calculator
from src.common import UserFriendlyException


def main() -> None:
    """
    Обязательнная составляющая программ, которые сдаются. Является точкой входа в приложение
    :return: Данная функция ничего не возвращает
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



if __name__ == "__main__":
    main()
