"""Abstract Syntax Tree (AST) node definitions for StepCalc.

This module defines the node hierarchy for the StepCalc language. Every node represents
a syntactic construct in the parsed source code.

In compliance with CMPSC 132 documentation standards, every class contains detailed
descriptions of all class and instance attributes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class ASTNode(ABC):
    """Abstract base class for all Abstract Syntax Tree nodes in StepCalc.

    Attributes:
        line (Optional[int]): Source line number where this node begins (1-indexed).
        column (Optional[int]): Source column number where this node begins (1-indexed).
    """

    line: Optional[int]
    column: Optional[int]

    def __init__(self, line: Optional[int] = None, column: Optional[int] = None) -> None:
        """Initialize an AST node with source coordinate metadata.

        Args:
            line: The 1-based line number in the source text where this node starts.
            column: The 1-based column number in the source text where this node starts.
        """
        self.line = line
        self.column = column

    @abstractmethod
    def __repr__(self) -> str:
        """Return a developer-readable representation of the AST node."""
        pass


class Number(ASTNode):
    """Represents an integer literal value in the program.

    Attributes:
        value (int): The integer value represented by this literal.
        line (Optional[int]): The source line number where the literal appears.
        column (Optional[int]): The source column number where the literal appears.
    """

    value: int

    def __init__(self, value: int, line: Optional[int] = None, column: Optional[int] = None) -> None:
        """Initialize an integer Number node.

        Args:
            value: The integer value.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.value = int(value)

    def __repr__(self) -> str:
        return f"Number({self.value})"


class Variable(ASTNode):
    """Represents a variable reference/identifier lookup.

    Attributes:
        name (str): The name/identifier of the variable being referenced.
        line (Optional[int]): The source line number where the variable identifier appears.
        column (Optional[int]): The source column number where the variable identifier appears.
    """

    name: str

    def __init__(self, name: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        """Initialize a Variable reference node.

        Args:
            name: The variable name string (e.g. 'x', 'total_count').
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.name = str(name)

    def __repr__(self) -> str:
        return f"Variable({self.name!r})"


class BinOp(ASTNode):
    """Represents a binary arithmetic operation between two expressions.

    Supported operators:
        '+'  : Integer Addition
        '-'  : Integer Subtraction
        '*'  : Integer Multiplication
        '/'  : Truncated Integer Division (floor towards zero)
        '%'  : Integer Modulo (remainder)
        '^'  : Integer Exponentiation (non-negative power)

    Attributes:
        left (ASTNode): The left-hand operand expression subtree.
        op (str): The binary operator string ('+', '-', '*', '/', '%', or '^').
        right (ASTNode): The right-hand operand expression subtree.
        line (Optional[int]): The source line number where the operator appears.
        column (Optional[int]): The source column number where the operator appears.
    """

    left: ASTNode
    op: str
    right: ASTNode

    def __init__(
        self,
        left: ASTNode,
        op: str,
        right: ASTNode,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize a binary operation node.

        Args:
            left: The left operand AST node.
            op: The arithmetic operator symbol.
            right: The right operand AST node.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"BinOp({self.left!r}, {self.op!r}, {self.right!r})"


class UnaryOp(ASTNode):
    """Represents a unary operation applied to an expression.

    Supported operators:
        '+' : Positive identity
        '-' : Arithmetic negation

    Attributes:
        op (str): The unary operator symbol ('+' or '-').
        operand (ASTNode): The expression to which the unary operator is applied.
        line (Optional[int]): The source line number where the unary operator appears.
        column (Optional[int]): The source column number where the unary operator appears.
    """

    op: str
    operand: ASTNode

    def __init__(
        self,
        op: str,
        operand: ASTNode,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize a unary operation node.

        Args:
            op: The unary operator symbol ('+' or '-').
            operand: The operand AST node being negated or confirmed positive.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryOp({self.op!r}, {self.operand!r})"


class Assignment(ASTNode):
    """Represents a variable assignment statement (e.g. `x = 5 + 3`).

    Attributes:
        name (str): The target variable name identifier.
        expr (ASTNode): The expression whose evaluated value will be assigned to the variable.
        line (Optional[int]): The source line number where assignment occurs.
        column (Optional[int]): The source column number where assignment occurs.
    """

    name: str
    expr: ASTNode

    def __init__(
        self,
        name: str,
        expr: ASTNode,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize an Assignment node.

        Args:
            name: The target variable identifier.
            expr: The expression AST node to evaluate and bind to the variable name.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.name = str(name)
        self.expr = expr

    def __repr__(self) -> str:
        return f"Assignment({self.name!r}, {self.expr!r})"


class ExplainCommand(ASTNode):
    """Represents an on-demand step-by-step explainer command (`explain <expr>`).

    Attributes:
        expr (ASTNode): The expression whose step-by-step reduction is to be displayed.
        line (Optional[int]): Source line number where the explain command was invoked.
        column (Optional[int]): Source column number where the explain command was invoked.
    """

    expr: ASTNode

    def __init__(
        self,
        expr: ASTNode,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize an ExplainCommand node.

        Args:
            expr: The expression AST node to trace and reduce step-by-step.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.expr = expr

    def __repr__(self) -> str:
        return f"ExplainCommand({self.expr!r})"


class TreeCommand(ASTNode):
    """Represents an on-demand AST visualizer command (`tree <expr>`).

    Attributes:
        expr (ASTNode): The expression whose Abstract Syntax Tree is to be printed.
        line (Optional[int]): Source line number where the tree command was invoked.
        column (Optional[int]): Source column number where the tree command was invoked.
    """

    expr: ASTNode

    def __init__(
        self,
        expr: ASTNode,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize a TreeCommand node.

        Args:
            expr: The expression AST node to visualize as an ASCII tree.
            line: Source line number.
            column: Source column number.
        """
        super().__init__(line, column)
        self.expr = expr

    def __repr__(self) -> str:
        return f"TreeCommand({self.expr!r})"
