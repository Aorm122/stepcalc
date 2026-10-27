"""Parser module for StepCalc.

Provides a clean interface for compiling source strings into AST nodes using Lark,
translating low-level Lark exceptions into user-friendly StepCalc errors.
"""

from typing import Optional
from lark import Lark, UnexpectedCharacters, UnexpectedToken, UnexpectedEOF

from stepcalc.grammar import STEPCALC_GRAMMAR
from stepcalc.transformer import ASTTransformer
from stepcalc.ast_nodes import ASTNode
from stepcalc.errors import LexerError, SyntaxFormatError


class Parser:
    """StepCalc parser that builds ASTs from source strings.

    Uses Lark with LALR(1) parsing. Zero manual if-else text processing.
    """

    def __init__(self) -> None:
        """Initialize the Lark parser instance and AST transformer."""
        self._lark = Lark(
            STEPCALC_GRAMMAR,
            parser="lalr",
            start="start",
            propagate_positions=True,
        )
        self._transformer = ASTTransformer()

    def parse(self, source: str) -> ASTNode:
        """Parse a source code string into an ASTNode.

        Args:
            source: The input source code string.

        Returns:
            The root ASTNode of the parsed program/statement.

        Raises:
            LexerError: If an invalid character is encountered.
            SyntaxFormatError: If the input violates the language grammar.
        """
        stripped = source.strip()
        if not stripped:
            raise SyntaxFormatError("Empty input.", source=source, hint="Type an arithmetic expression or command.")

        try:
            tree = self._lark.parse(stripped)
            return self._transformer.transform(tree)

        except UnexpectedCharacters as e:
            raise LexerError(
                f"Unexpected character '{e.char}'",
                line=e.line,
                column=e.column,
                source=source,
                hint="Only integers, variable names, arithmetic symbols (+, -, *, /, %, ^), and parentheses are allowed.",
            ) from e

        except UnexpectedEOF as e:
            raise SyntaxFormatError(
                "Incomplete expression (unexpected end of input).",
                line=getattr(e, "line", 1),
                column=getattr(e, "column", len(source)),
                source=source,
                hint="Did you leave an expression incomplete or forget a closing parenthesis ')'?",
            ) from e

        except UnexpectedToken as e:
            token = e.token
            hint = "Check your expression syntax for correct formatting."
            val = str(token.value) if token else "token"

            if val in ("+", "-", "*", "/", "%", "^"):
                hint = f"Operator '{val}' is placed unexpectedly. Did you miss a number before or after it?"
            elif val == ")":
                hint = "Unmatched closing parenthesis ')' without a preceding '('."
            elif token.type == "CNAME":
                hint = f"Unexpected identifier '{val}'. Missing an operator between values?"
            elif token.type == "INT":
                hint = f"Unexpected number '{val}'. Missing an operator between numbers?"

            raise SyntaxFormatError(
                f"Unexpected token '{val}'",
                line=token.line if token else 1,
                column=token.column if token else len(source),
                source=source,
                hint=hint,
            ) from e
