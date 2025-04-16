import uuid


class User:
    def __init__(self, id_user: uuid.UUID, name: str, login: str, password: str = None):
        self.id = id_user
        self.name = name
        self.login = login
        self.password = password


def create_user(
    id_user: uuid.UUID, name: str = None, login: str = None, password: str = None
):
    return User(id_user, name, login, password)
