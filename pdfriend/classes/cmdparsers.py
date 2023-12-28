import pdfriend.classes.exceptions as exceptions

class CmdParser:
    def __init__(self, cmd_name: str, args: list[str]):
        self.cmd_name = cmd_name
        self.args = args
        self.current_arg = 1

    def next_str(self):
        if len(self.args) == 0:
            raise exceptions.ExpectedError(
                f"argument {self.current_arg} for command \"{self.cmd_name}\" not provided"
            )

        head, tail = self.args[0], self.args[1:]
        self.args = tail
        self.current_arg += 1

        return head

    def next_str_or(self, default: str) -> str:
        try:
            return self.next_str()
        except Exception:
            return default

    def next_typed(self, type_name: str, type_converter):
        if len(self.args) == 0:
            raise exceptions.ExpectedError(
                f"argument {self.current_arg} for command \"{self.cmd_name}\" not provided"
            )

        head, tail = self.args[0], self.args[1:]
        self.args = tail

        try:
            result = type_converter(head)
            # moved the incrementing here so that it doesn't fire before the exception
            self.current_arg += 1
            return result
        except Exception:
            raise exceptions.ExpectedError(
                f"argument {self.current_arg} for command \"{self.cmd_name}\" (value: {head}) could not be converted to type \"{type_name}\""
            )

    def next_int(self):
        return self.next_typed("int", int)
