import pdfriend.classes.wrappers as wrappers
import pdfriend.classes.exceptions as exceptions
import pdfriend.classes.cmdparsers as cmdparsers
import pdfriend.classes.info as info
from pdfriend.classes.platforms import Platform
from pdfriend.classes.config import Config
import pdfriend.utils as utils
import pathlib
import re


whitespace_pattern = re.compile(r"\s+")

def parse_command_string(command_string: str) -> list[str]:
    return re.split(whitespace_pattern, command_string)

program_info = info.ProgramInfo(
    info.CommandInfo("help", "h", descr = """[command?]
    display help message. If given a command, it will only display the help message for that command.

    examples:
        help rotate
            displays the help blurb for the rotate command
        help exit
            displays the help blurb for the exit command
    """),
    info.CommandInfo("exit", "e", descr = """
    exits the edit mode
    """),
    info.CommandInfo("rotate", "r", descr = """[page_numbers] [angle]
    rotates page clockwise with the given numbers (starting from 1) by the given angle (in degrees). Can use negative angles to rotate counter-clockwise. DO NOT put extra spaces between the page numbers!

    examples:
        r 34 1.2
            rotates page 34 clockwise by 1.2 degrees
        r 1,3,8 -4
            rotates pages 1,3 and 8 counter-clockwise by 4 degrees
        r 3:18 90
            rotates pages 3 through 18 (INCLUDING 18) clockwise by 90 degrees
        r 1,13,5:7,2 54
            rotates pages 1,2,5,6,7,13 clockwise by 54 degrees
        r all -90
            rotates all pages counter-clockwise by 90 degrees
    """),
    info.CommandInfo("delete", "d", descr = """[page_numbers]
    deletes all specified pages. DO NOT put extra spaces between the page numbers!

    examples:
        d 7
            deletes page 7
        d 4,8,1
            deletes pages 1, 4 and 8
        d 6:66
            deletes pages 6 through 66 (INCLUDING 66)
        d :13
            deletes all pages up to and including 13
        d 4,17,3:6
            deletes pages 3,4,5,6 and 17
    """),
    info.CommandInfo("swap", "s", descr = """[page_0] [page_1]
    swaps page_0 and page_1.
    """),
    info.CommandInfo("move", "m", descr = """[source] [destination]
    move source to BEFORE destination, taking its place.

    examples:
        m 3 17
            moves page 3 to page 17, pushing back the pages from 17 onward
        m 83 1
            moves page 83 to the beginning of the document
    """),
    info.CommandInfo("push", "p", descr = """[pages] [offset]
    pushes the specified pages by offset pages (offset can be negative).

    examples:
        p 3 7
            moves page 3 to 7 pages down, i.e. to page 10.
        p 4,9,2 1
            moves pages 2,4,9 by 1 page.
        p 5:8 -3
            moves pages 5,6,7,8 to 3 pages BACK.
        p 5,6,90:94 5
            moves pages 5,6,90,91,92,93,94 to be 5 pages down.
        p :5 4
            moves pages 1,2,3,4,5 to be 4 pages down.
        p 67: -7
            move pages from 67 to the end of the PDF to be 7 pages back.
        p 70: 5
            FAILS. 70: includes the end of the PDF, and you can't move that further down.
    """),
    info.CommandInfo("undo", "u", descr = """[number?]
    undo the previous [number] commands.

    examples:
        u
            undoes the previous command
        u 3
            undoes the previous 3 commands
        u all
            undoes all commands issued this session (reverts document fully)
    """),
    info.CommandInfo("export", "x", descr = """[filename?=pdfriend_edit.txt]
    exports all the commands you ran into a text file

        examples:
            x
                exports your commands to pdfriend_edit.txt
            x out.txt
                exports your commands to out.txt
    """),
    foreword = "pdfriend edit shell for quick changes. Commands:",
    postword = "use h [command] to learn more about a specific command"
)


def run_edit_command(pdf: wrappers.PDFWrapper, args: list[str]):
    cmd_parser = cmdparsers.CmdParser.FromArgs(
        program_info,
        args,
        no_command_message = "No command specified! Type h or help for a list of the available commands"
    )
    short = cmd_parser.short()

    if short == "h":
        subcommand = cmd_parser.next_str_or(None)
        print(program_info.help(subcommand))

        # this is to prevent rewriting the file and appending
        # the command to the command stack
        raise exceptions.ShellContinue()
    elif short == "e":
        raise exceptions.ShellExit()
    elif short == "r":
        pages = cmd_parser.next_pdf_slice()
        angle = cmd_parser.next_float("angle")

        if len(pages) == 0:
            return
        # the slice is sorted, so if any pages are out of range, it'll
        # either be the first or the last one, probably the last
        pdf.raise_if_out_of_range(pages[-1])
        pdf.raise_if_out_of_range(pages[0])

        for page in pages:
            pdf.rotate_page(page, angle)
    elif short == "d":
        pages = cmd_parser.next_pdf_slice()

        for page in pages:
            pdf.pop_page(page)
    elif short == "s":
        page_0 = cmd_parser.next_int("page_0")
        pdf.raise_if_out_of_range(page_0)
        page_1 = cmd_parser.next_int("page_1")
        pdf.raise_if_out_of_range(page_1)

        pdf.swap_pages(page_0, page_1)
    elif short == "m":
        source = cmd_parser.next_int("source")
        pdf.raise_if_out_of_range(source)
        destination = cmd_parser.next_int("destination")
        pdf.raise_if_out_of_range(destination)

        page = pdf.pages.pop(source - 1)
        pdf.pages.insert(destination - 1, page)
    elif short == "p":
        pages = cmd_parser.next_pdf_slice()
        offset = cmd_parser.next_int("offset")

        last_page_before = pages[-1]
        last_page_after = last_page_before + offset

        if last_page_after > pdf.len(): # only check last page, as the slice is sorted
            raise exceptions.ExpectedError(
                f"can't move page {last_page_before} to {last_page_after}, as it's outside the PDF (number of pages: {pdf.len()})"
            )

        if offset > 0:
            pages = pages[::-1]

        for page in pages:
            p = pdf.pages.pop(page - 1)
            pdf.pages.insert(page + offset - 1, p)
    elif short == "u":
        # arg will be converted to int, unless it's "all". Defaults to 1
        num_of_commands = cmd_parser.next_typed_or(
            "int or \"all\"", lambda s: s if s == "all" else int(s),
            1 # default value
        )

        raise exceptions.ShellUndo(num_of_commands)
    elif short == "x":
        filename = cmd_parser.next_str_or("pdfriend_edit.txt")

        raise exceptions.ShellExport(filename)


def edit(infile: str):
    pdf = wrappers.PDFWrapper.Read(infile)
    command_stack = []

    # backup the file, because it will be overwritten
    backup_path = pdf.backup(infile)
    print(f"editing {infile}\nbackup created in {backup_path}")

    while True:
        try:
            args = parse_command_string(input(""))
            run_edit_command(pdf, args)
            command_stack.append(args)

            pdf.write(infile) # overwrites the file!
        except (KeyboardInterrupt, exceptions.ShellExit):
            return
        except exceptions.ShellContinue:
            continue
        except exceptions.ShellUndo as undo:
            if undo.num == "all":
                command_stack = []
            else:
                command_stack = command_stack[:-undo.num]

            pdf = wrappers.PDFWrapper.Read(backup_path)
            for args in command_stack:
                run_edit_command(pdf, args)

            pdf.write(infile)
        except exceptions.ShellExport as export:
            with open(export.filename, "w") as outfile:
                outfile.write("\n".join([
                    " ".join(args) for args in command_stack
                ]))
        except exceptions.ExpectedError as e:
            print(e)
        except Exception as e:
            utils.print_unexpected_exception(e, Config.Debug)

