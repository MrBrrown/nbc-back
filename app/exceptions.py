class SqlException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class DuplicateException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
