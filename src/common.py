from typing import TypeAlias


class UserFriendlyException(Exception):
    pass


class InvalidIdentifierError(Exception):
    pass


Nametable: TypeAlias = dict[str, float]
