from types import SimpleNamespace

default_flags = dict(
    help = False,
    version = False,
    debug = False,
    output = "pdfriend_output",
    inplace = False,
    quality = 100,
    get = None,
    set = None,
    pop = None
)
default_flags["import"] = None


def make_args(commands: list[str], **kwargs):
    return SimpleNamespace(
        commands = commands,
        **(default_flags | kwargs)
    )
