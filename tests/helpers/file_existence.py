from pdfriend.main import run_pdfriend
from helpers.flags import make_args
from pathlib import Path


def check_existence(*paths: str|Path, remove: bool = False) -> bool:
    paths = [Path(path) for path in paths]

    checks = [path.exists() for path in paths]

    if remove:
        for path in paths:
            if path.exists():
                path.unlink()

    return all(checks)


# checks whether the -o and -i flags work properly in a single output command
def check_one_output_command(
    commands: list[str],
    input: str|Path,
    default_output: str|Path = "pdfriend_output.pdf",
    forced_output: str|Path = "forced_output.pdf",
    **kwargs
) -> bool:
    checks = []
    run_pdfriend(make_args(commands, **kwargs))
    checks.append(check_existence(default_output, remove = True))

    run_pdfriend(make_args(commands, output = forced_output, **kwargs))
    checks.append(check_existence(forced_output, remove = True))

    run_pdfriend(make_args(commands, inplace = True, **kwargs))
    checks.append(check_existence(input, remove = True))

    return all(checks)
