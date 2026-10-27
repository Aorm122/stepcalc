"""Main entry point for the StepCalc Programming Language.

Supports interactive REPL shell, file execution (.calc), and single-expression evaluation.
"""

import sys
import argparse
from stepcalc import __version__
from stepcalc.repl import StepCalcREPL
from stepcalc.errors import StepCalcError


def main() -> None:
    """Parse command line arguments and execute StepCalc."""
    parser = argparse.ArgumentParser(
        prog="stepcalc",
        description="StepCalc: Educational Arithmetic Language with Step-by-Step Reduction & AST Visualizer.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Optional path to a .calc script file to execute.",
    )
    parser.add_argument(
        "-e", "--eval",
        dest="eval_expr",
        metavar="EXPR",
        help="Evaluate a single StepCalc expression or command and exit.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"StepCalc v{__version__}",
    )

    args = parser.parse_args()
    repl = StepCalcREPL()

    if args.eval_expr:
        try:
            output = repl.run_line(args.eval_expr)
            if output:
                print(output)
        except StepCalcError as e:
            print(e.format_diagnostic(), file=sys.stderr)
            sys.exit(1)
    elif args.file:
        repl.run_file(args.file)
    else:
        repl.start_repl()


if __name__ == "__main__":
    main()
