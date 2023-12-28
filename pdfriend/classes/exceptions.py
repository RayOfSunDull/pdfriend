class ShellExit(Exception):
    pass

class ShellContinue(Exception):
    pass

class ShellUndo(Exception):
    def __init__(self, num: str | int):
        self.num = num
        super().__init__()

class ExpectedError(Exception):
    pass
