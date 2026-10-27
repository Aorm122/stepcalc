"""Error hierarchy and visual diagnostic formatting for StepCalc.

This module provides custom exception classes for lexical, syntactic, and runtime errors,
along with pretty caret-pointer (^^^) formatting for user-friendly error diagnostics.
"""

from typing import Optional


class StepCalcError(Exception):
    """Base exception class for all errors in the StepCalc language.

    Attributes:
        message (str): A human-readable description of the error.
        line (Optional[int]): 1-based source line number where the error occurred.
        column (Optional[int]): 1-based source column number where the error occurred.
        source (Optional[str]): The original source code string that caused the error.
        hint (Optional[str]): An actionable suggestion on how to fix the error.
    """

    message: str
    line: Optional[int]
    column: Optional[int]
    source: Optional[str]
    hint: Optional[str]

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> None:
        """Initialize a StepCalc error.

        Args:
            message: Description of the error.
            line: Line number where error occurred.
            column: Column number where error occurred.
            source: The full source code snippet or line.
            hint: Helpful tip for the user.
        """
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        self.hint = hint

    def format_diagnostic(self) -> str:
        """Format the error with visual caret indicators and helpful hints.

        Returns:
            A formatted multi-line string suitable for terminal display.
        """
        lines = []
        loc = ""
        if self.line is not None and self.column is not None:
            loc = f" [Line {self.line}, Col {self.column}]"
        elif self.line is not None:
            loc = f" [Line {self.line}]"

        lines.append(f"Error{loc}: {self.message}")

        if self.source is not None and self.column is not None:
            source_lines = self.source.splitlines()
            line_idx = (self.line - 1) if (self.line and self.line <= len(source_lines)) else 0
            if 0 <= line_idx < len(source_lines):
                target_line = source_lines[line_idx]
                prefix = "  Input:  "
                lines.append(f"{prefix}{target_line}")
                caret_pos = max(1, self.column)
                caret_indent = " " * (len(prefix) + caret_pos - 1)
                lines.append(f"{caret_indent}^")

        if self.hint:
            lines.append(f"  Hint:   {self.hint}")

        return "\n".join(lines)


class LexerError(StepCalcError):
    """Raised when an unrecognized character or token is encountered."""
    pass


class SyntaxFormatError(StepCalcError):
    """Raised when the input violates the language grammar (incorrect format)."""
    pass


class RuntimeEvaluationError(StepCalcError):
    """Base class for errors occurring during AST evaluation."""
    pass


class DivisionByZeroError(RuntimeEvaluationError):
    """Raised when attempting integer division or modulo by zero."""
    pass


class NegativeExponentError(RuntimeEvaluationError):
    """Raised when attempting an integer exponentiation with a negative power."""
    pass


class UndefinedVariableError(RuntimeEvaluationError):
    """Raised when referencing a variable that has not been defined."""
    pass
