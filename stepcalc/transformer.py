"""AST Transformer for StepCalc.

Transforms Lark parse trees into strongly-typed AST nodes (defined in ast_nodes.py)
without any if-else text processing.
"""

from typing import List, Any
from lark import Transformer, Token, Tree
from stepcalc.ast_nodes import (
    ASTNode,
    Number,
    Variable,
    BinOp,
    UnaryOp,
    Assignment,
    ExplainCommand,
    TreeCommand,
)


class ASTTransformer(Transformer):
    """Transformer that converts Lark parse tree nodes into StepCalc ASTNode objects.

    Each method corresponds directly to a rule name or rule alias in the Lark grammar.
    """

    def number(self, items: List[Any]) -> Number:
        token = items[0]
        line = token.line if isinstance(token, Token) else None
        col = token.column if isinstance(token, Token) else None
        return Number(int(token), line=line, column=col)

    def variable(self, items: List[Any]) -> Variable:
        token = items[0]
        line = token.line if isinstance(token, Token) else None
        col = token.column if isinstance(token, Token) else None
        return Variable(str(token), line=line, column=col)

    def add(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="+", right=items[1])

    def sub(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="-", right=items[1])

    def mul(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="*", right=items[1])

    def div(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="/", right=items[1])

    def mod(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="%", right=items[1])

    def pow(self, items: List[Any]) -> BinOp:
        return BinOp(left=items[0], op="^", right=items[1])

    def pos(self, items: List[Any]) -> UnaryOp:
        return UnaryOp(op="+", operand=items[0])

    def neg(self, items: List[Any]) -> UnaryOp:
        return UnaryOp(op="-", operand=items[0])

    def assignment(self, items: List[Any]) -> Assignment:
        var_token = items[0]
        expr_node = items[1]
        line = var_token.line if isinstance(var_token, Token) else None
        col = var_token.column if isinstance(var_token, Token) else None
        return Assignment(name=str(var_token), expr=expr_node, line=line, column=col)

    def explain_cmd(self, items: List[Any]) -> ExplainCommand:
        return ExplainCommand(expr=items[0])

    def tree_cmd(self, items: List[Any]) -> TreeCommand:
        return TreeCommand(expr=items[0])
