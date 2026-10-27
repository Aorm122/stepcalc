"""Interactive REPL (Read-Eval-Print Loop) and script execution engine for StepCalc.

Provides a rich terminal experience with formatted prompts, symbols, spacing,
and comprehensive error recovery to ensure the program executes without crashes.
"""

import sys
from typing import Optional, List
from stepcalc.parser import Parser
from stepcalc.evaluator import Evaluator, StepTracer, ASTVisualizer
from stepcalc.ast_nodes import ExplainCommand, TreeCommand, Assignment
from stepcalc.errors import StepCalcError


BANNER = r"""
========================================================================
   ____  _                ____      _      
  / ___|| |_ ___ _ __    / ___|__ _| | ___ 
  \___ \| __/ _ \ '_ \  | |   / _` | |/ __|
   ___) | ||  __/ |_) | | |__| (_| | | (__ 
  |____/ \__\___| .__/   \____\__,_|_|\___|
                |_|                        
  StepCalc: Educational Arithmetic Language (v1.0.0)
  CMPSC 132: Programming Languages - Final Project
========================================================================
  Commands:
    <expr>           Evaluate arithmetic expression (e.g. 10 + 5 * 2)
    <var> = <expr>   Assign an integer variable (e.g. x = 20)
    explain <expr>   Show step-by-step math reduction & derivation
    tree <expr>      Display Abstract Syntax Tree (AST)
    :vars            List all currently defined variables
    :reset           Clear all stored variables
    :help            Show this help guide
    :exit            Exit the StepCalc shell
========================================================================
"""

HELP_TEXT = """
StepCalc Syntax Guide:
------------------------------------------------------------------------
  Supported Operators (in order of PEMDAS precedence):
    1. Parentheses:        ( expr )
    2. Exponentiation:     ^       (right-associative, non-negative)
    3. Unary Signs:        +expr, -expr
    4. Multiplicative:     *, /, % (integer floor division & modulo)
    5. Additive:           +, -    (integer addition & subtraction)
    6. Assignment:         var = expr

  Unique Commands:
    explain (2 + 3) * 4    Step-by-step reduction trace
    tree (x + 5) ^ 2       Visual ASCII AST representation

  Meta Commands:
    :vars                  Inspect symbol table environment
    :reset                 Reset all variable bindings
    :clear                 Clear terminal screen
    :help                  Display this reference
    :exit or :quit         Quit the application
------------------------------------------------------------------------
"""


class StepCalcREPL:
    """Interactive command-line shell for StepCalc.

    Attributes:
        parser (Parser): Lark-based parser engine.
        evaluator (Evaluator): Evaluator managing the runtime environment.
        tracer (StepTracer): Step-by-step reduction tracer.
    """

    parser: Parser
    evaluator: Evaluator
    tracer: StepTracer

    def __init__(self, parser: Optional[Parser] = None, evaluator: Optional[Evaluator] = None) -> None:
        """Initialize the REPL instance."""
        self.parser = parser if parser is not None else Parser()
        self.evaluator = evaluator if evaluator is not None else Evaluator()
        self.tracer = StepTracer(self.evaluator)

    def run_line(self, line_text: str) -> Optional[str]:
        """Execute a single line of input.

        Args:
            line_text: The raw input string.

        Returns:
            Formatted string output if any, or None.
        """
        raw = line_text.strip()
        if not raw or raw.startswith("#"):
            return None

        # Check meta commands
        if raw in (":exit", ":quit"):
            print("\nExiting StepCalc. Goodbye!")
            sys.exit(0)
        elif raw == ":help":
            return HELP_TEXT
        elif raw == ":vars":
            vars_dict = self.evaluator.env.list_all()
            if not vars_dict:
                return "  (No variables currently defined)"
            lines = ["  Active Variables:"]
            for k, v in sorted(vars_dict.items()):
                lines.append(f"    {k} = {v}")
            return "\n".join(lines)
        elif raw == ":reset":
            self.evaluator.env.clear()
            return "  [Environment reset: all variables cleared]"
        elif raw == ":clear":
            print("\033[H\033[J", end="")
            return None

        # Parse and execute through AST
        node = self.parser.parse(raw)

        if isinstance(node, ExplainCommand):
            steps = self.tracer.trace(node.expr)
            final_val = self.evaluator.evaluate(node.expr)
            out_lines = ["  Explanation:"]
            if not steps:
                out_lines.append(f"    Single Value: {final_val}")
            else:
                for idx, (expr_str, desc) in enumerate(steps, 1):
                    out_lines.append(f"    Step {idx}: {expr_str:<20} [{desc}]")
                out_lines.append(f"    Result: {final_val}")
            return "\n".join(out_lines)

        elif isinstance(node, TreeCommand):
            tree_str = ASTVisualizer.render(node.expr)
            return f"  Abstract Syntax Tree:\n{tree_str}"

        elif isinstance(node, Assignment):
            val = self.evaluator.evaluate(node)
            return f"  [assigned] {node.name} = {val}"

        else:
            val = self.evaluator.evaluate(node)
            return f"  => {val}"

    def start_repl(self) -> None:
        """Launch the interactive REPL shell."""
        print(BANNER)
        while True:
            try:
                user_input = input("calc> ")
                output = self.run_line(user_input)
                if output:
                    print(output)
                    print()
            except KeyboardInterrupt:
                print("\n  KeyboardInterrupt (Type :exit to quit)")
            except EOFError:
                print("\nExiting StepCalc. Goodbye!")
                break
            except StepCalcError as err:
                print()
                print(err.format_diagnostic())
                print()
            except Exception as ex:
                print(f"\n  Unexpected Error: {ex}\n")

    def run_file(self, filepath: str) -> None:
        """Execute a StepCalc (.calc) script file line-by-line.

        Args:
            filepath: Path to the script file.
        """
        print(f"Executing StepCalc script: {filepath}")
        print("=" * 60)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"Error opening file '{filepath}': {e}")
            sys.exit(1)

        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            print(f"[{line_num}] > {stripped}")
            try:
                output = self.run_line(stripped)
                if output:
                    print(output)
            except StepCalcError as err:
                # Attach file line number
                err.line = line_num
                err.source = stripped
                print(err.format_diagnostic())
                print()
            except Exception as ex:
                print(f"  Error on line {line_num}: {ex}\n")
        print("=" * 60)
        print("Script execution completed.")
