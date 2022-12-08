class RunTimeError(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        # self.msg = msg

class Return_exception(RunTimeError):
    def __init__(self, value):
        self.value = value