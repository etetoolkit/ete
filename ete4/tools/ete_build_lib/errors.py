class ConfigError(ValueError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        # return repr(self.value)
        return self.value


class DataError(ValueError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        # return repr(self.value)
        return self.value

class TaskError(ValueError):
    def __init__(self, value, msg=""):
        self.value = value
        self.msg = msg
    def __str__(self):
        return str(self.msg)

class SgeError(ValueError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        # return repr(self.value)
        return self.value
