"""Evaluation engine, environment, step-by-step reduction tracer, and AST visualizer for StepCalc.

This module implements the semantic evaluation phase of the StepCalc language:
- Environment: stores and manages variable bindings.
- Evaluator: walks the AST and calculates integer results.
- StepTracer: step-by-step reduction engine that demonstrates how expressions evaluate.
- ASTVisualizer: renders ASTs into readable ASCII hierarchy trees.
"""

from typing import Dict, List, Tuple, Optional, Any
import copy

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
from stepcalc.errors import (
    DivisionByZeroError,
    NegativeExponentError,
    UndefinedVariableError,
    RuntimeEvaluationError,
)


class Environment:
    """Symbol table holding variable bindings during program execution.

    Attributes:
        variables (Dict[str, int]): Dictionary mapping variable identifiers to integer values.
    """

    variables: Dict[str, int]

    def __init__(self) -> None:
        """Initialize an empty Environment."""
        self.variables = {}

    def get(self, name: str, line: Optional[int] = None, col: Optional[int] = None) -> int:
        """Retrieve a variable's value from the environment.

        Args:
            name: The variable identifier.
            line: Source line coordinate for error reporting.
            col: Source column coordinate for error reporting.

        Returns:
            The stored integer value.

        Raises:
            UndefinedVariableError: If the variable has not been defined.
        """
        if name not in self.variables:
            raise UndefinedVariableError(
                f"Undefined variable '{name}'.",
                line=line,
                column=col,
                hint=f"Define it first using '{name} = <number or expression>'.",
            )
        return self.variables[name]

    def set(self, name: str, value: int) -> None:
        """Bind or re-bind a variable identifier to an integer value.

        Args:
            name: The variable identifier.
            value: The integer value to store.
        """
        self.variables[name] = int(value)

    def list_all(self) -> Dict[str, int]:
        """Return a copy of all current variable bindings."""
        return dict(self.variables)

    def clear(self) -> None:
        """Clear all stored variables from the environment."""
        self.variables.clear()


def ast_to_str(node: ASTNode, parent_prec: int = 0) -> str:
    """Convert an AST node back into a readable mathematical expression string.

    Automatically places parentheses only where necessary according to precedence.

    Args:
        node: The AST node to format.
        parent_prec: The operator precedence level of the parent node.

    Returns:
        A human-readable string representation of the expression.
    """
    prec_map = {
        "+": 1, "-": 1,
        "*": 2, "/": 2, "%": 2,
        "^": 3,
    }

    if isinstance(node, Number):
        return str(node.value)

    if isinstance(node, Variable):
        return node.name

    if isinstance(node, UnaryOp):
        inner = ast_to_str(node.operand, parent_prec=4)
        res = f"{node.op}{inner}"
        return f"({res})" if parent_prec > 4 else res

    if isinstance(node, BinOp):
        my_prec = prec_map.get(node.op, 0)
        # For right-associative '^', left side binds tighter; for left-associative, right side binds tighter
        left_prec = my_prec if node.op != "^" else my_prec + 1
        right_prec = my_prec + 1 if node.op != "^" else my_prec

        left_str = ast_to_str(node.left, left_prec)
        right_str = ast_to_str(node.right, right_prec)

        res = f"{left_str} {node.op} {right_str}"
        return f"({res})" if my_prec < parent_prec else res

    if isinstance(node, Assignment):
        return f"{node.name} = {ast_to_str(node.expr, 0)}"

    return str(node)


class Evaluator:
    """Evaluates StepCalc AST nodes into integer results.

    Attributes:
        env (Environment): The symbol table environment used for variable storage.
    """

    env: Environment

    def __init__(self, env: Optional[Environment] = None) -> None:
        """Initialize the evaluator.

        Args:
            env: Optional existing Environment. If None, a fresh one is created.
        """
        self.env = env if env is not None else Environment()

    def evaluate(self, node: ASTNode) -> int:
        """Evaluate an AST expression node and return its computed integer value.

        Args:
            node: The ASTNode to evaluate.

        Returns:
            The integer result of the computation.

        Raises:
            DivisionByZeroError: If a division or modulo by zero is attempted.
            NegativeExponentError: If an integer is raised to a negative power.
            UndefinedVariableError: If an unbound variable is referenced.
            RuntimeEvaluationError: For other evaluation errors.
        """
        if isinstance(node, Number):
            return node.value

        if isinstance(node, Variable):
            return self.env.get(node.name, line=node.line, col=node.column)

        if isinstance(node, UnaryOp):
            val = self.evaluate(node.operand)
            if node.op == "+":
                return val
            elif node.op == "-":
                return -val
            raise RuntimeEvaluationError(f"Unknown unary operator: {node.op}", line=node.line, column=node.column)

        if isinstance(node, BinOp):
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)

            if node.op == "+":
                return left_val + right_val
            elif node.op == "-":
                return left_val - right_val
            elif node.op == "*":
                return left_val * right_val
            elif node.op == "/":
                if right_val == 0:
                    raise DivisionByZeroError(
                        "Cannot divide by zero.",
                        line=node.line,
                        column=node.column,
                        hint="The divisor expression evaluated to 0. Change the divisor to a non-zero integer.",
                    )
                return left_val // right_val
            elif node.op == "%":
                if right_val == 0:
                    raise DivisionByZeroError(
                        "Cannot compute modulo by zero.",
                        line=node.line,
                        column=node.column,
                        hint="Modulo operator requires a non-zero divisor.",
                    )
                return left_val % right_val
            elif node.op == "^":
                if right_val < 0:
                    raise NegativeExponentError(
                        f"Negative exponent '{right_val}' is invalid in integer arithmetic.",
                        line=node.line,
                        column=node.column,
                        hint="StepCalc is an integer language. Exponents must be non-negative (>= 0).",
                    )
                return left_val ** right_val
            else:
                raise RuntimeEvaluationError(f"Unknown operator: {node.op}", line=node.line, column=node.column)

        if isinstance(node, Assignment):
            val = self.evaluate(node.expr)
            self.env.set(node.name, val)
            return val

        raise RuntimeEvaluationError(f"Cannot evaluate AST node of type {type(node).__name__}")


class StepTracer:
    """Step-by-step reduction engine for StepCalc expressions.

    Traces the sequential reduction of an expression AST into simpler sub-expressions
    until reaching a final integer result.
    """

    evaluator: Evaluator

    def __init__(self, evaluator: Evaluator) -> None:
        """Initialize the StepTracer with an evaluator.

        Args:
            evaluator: The active Evaluator with access to the current environment.
        """
        self.evaluator = evaluator

    def trace(self, root_node: ASTNode) -> List[Tuple[str, str]]:
        """Trace the reduction steps of an expression.

        Args:
            root_node: The root ASTNode to trace.

        Returns:
            A list of tuples (step_expression_string, explanation_of_action).
        """
        steps: List[Tuple[str, str]] = []
        current_ast = copy.deepcopy(root_node)

        # Record initial state
        initial_expr = ast_to_str(current_ast)

        # Loop reducing one innermost reducible operation per step
        max_steps = 100
        step_count = 0

        while step_count < max_steps:
            reduced, next_ast, action_desc = self._reduce_one_step(current_ast)
            if not reduced:
                break
            step_count += 1
            next_expr = ast_to_str(next_ast)
            steps.append((next_expr, action_desc))
            current_ast = next_ast

        return steps

    def _reduce_one_step(self, node: ASTNode) -> Tuple[bool, ASTNode, str]:
        """Attempt to perform a single reduction on the leftmost innermost sub-expression.

        Returns:
            (reduced_bool, new_ast_node, action_description)
        """
        if isinstance(node, Number):
            return False, node, ""

        if isinstance(node, Variable):
            val = self.evaluator.env.get(node.name, line=node.line, col=node.column)
            desc = f"lookup '{node.name}' = {val}"
            return True, Number(val, line=node.line, column=node.column), desc

        if isinstance(node, UnaryOp):
            if isinstance(node.operand, Number):
                val = self.evaluator.evaluate(node)
                desc = f"evaluate '{node.op}{node.operand.value}' = {val}"
                return True, Number(val, line=node.line, column=node.column), desc
            else:
                reduced, new_op, desc = self._reduce_one_step(node.operand)
                if reduced:
                    return True, UnaryOp(node.op, new_op, line=node.line, column=node.column), desc

        if isinstance(node, BinOp):
            # If left is not a number, reduce left first
            if not isinstance(node.left, Number):
                reduced, new_left, desc = self._reduce_one_step(node.left)
                if reduced:
                    return True, BinOp(new_left, node.op, node.right, line=node.line, column=node.column), desc

            # If left is a number but right is not, reduce right
            if not isinstance(node.right, Number):
                reduced, new_right, desc = self._reduce_one_step(node.right)
                if reduced:
                    return True, BinOp(node.left, node.op, new_right, line=node.line, column=node.column), desc

            # Both left and right are Numbers! Perform this binary operation
            val = self.evaluator.evaluate(node)
            desc = f"compute '{node.left.value} {node.op} {node.right.value}' = {val}"
            return True, Number(val, line=node.line, column=node.column), desc

        return False, node, ""


class ASTVisualizer:
    """Renders AST nodes as a formatted ASCII tree structure."""

    @staticmethod
    def render(node: ASTNode, prefix: str = "", is_last: bool = True) -> str:
        """Render an AST node and all its children as an ASCII tree.

        Uses universal ASCII characters (+--, \\--, |) for guaranteed cross-platform
        rendering on all operating systems and Windows console code pages.

        Args:
            node: The root ASTNode to render.
            prefix: Formatting prefix for current indentation level.
            is_last: Whether this node is the last sibling in its parent's child list.

        Returns:
            A formatted multi-line ASCII tree string.
        """
        lines = []
        connector = "\\-- " if is_last else "+-- "

        if isinstance(node, Number):
            lines.append(f"{prefix}{connector}Number: {node.value}")
        elif isinstance(node, Variable):
            lines.append(f"{prefix}{connector}Variable: {node.name}")
        elif isinstance(node, UnaryOp):
            lines.append(f"{prefix}{connector}UnaryOp: {node.op}")
            new_prefix = prefix + ("    " if is_last else "|   ")
            lines.append(ASTVisualizer.render(node.operand, new_prefix, True))
        elif isinstance(node, BinOp):
            lines.append(f"{prefix}{connector}BinOp: {node.op}")
            new_prefix = prefix + ("    " if is_last else "|   ")
            lines.append(ASTVisualizer.render(node.left, new_prefix, False))
            lines.append(ASTVisualizer.render(node.right, new_prefix, True))
        elif isinstance(node, Assignment):
            lines.append(f"{prefix}{connector}Assignment: {node.name}")
            new_prefix = prefix + ("    " if is_last else "|   ")
            lines.append(ASTVisualizer.render(node.expr, new_prefix, True))
        elif isinstance(node, ExplainCommand):
            lines.append(f"{prefix}{connector}Command: explain")
            new_prefix = prefix + ("    " if is_last else "|   ")
            lines.append(ASTVisualizer.render(node.expr, new_prefix, True))
        elif isinstance(node, TreeCommand):
            lines.append(f"{prefix}{connector}Command: tree")
            new_prefix = prefix + ("    " if is_last else "|   ")
            lines.append(ASTVisualizer.render(node.expr, new_prefix, True))
        else:
            lines.append(f"{prefix}{connector}{type(node).__name__}")

        return "\n".join(lines)
