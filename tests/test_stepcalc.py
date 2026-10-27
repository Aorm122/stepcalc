"""Comprehensive test suite for StepCalc.

Tests coverage:
- Lexer and parser compliance
- Arithmetic operator precedence & associativity (PEMDAS/BODMAS)
- Unary operators and nested parentheses
- Variable assignment and scoping
- Formatting and syntax error detection
- Runtime exception handling (division by zero, negative exponent, undefined variable)
- Step-by-step reduction tracer
- AST visualizer
"""

import pytest
from stepcalc.parser import Parser
from stepcalc.evaluator import Evaluator, StepTracer, ASTVisualizer
from stepcalc.errors import (
    StepCalcError,
    LexerError,
    SyntaxFormatError,
    DivisionByZeroError,
    NegativeExponentError,
    UndefinedVariableError,
)
from stepcalc.repl import StepCalcREPL


@pytest.fixture
def parser() -> Parser:
    """Fixture providing a fresh Parser instance."""
    return Parser()


@pytest.fixture
def evaluator() -> Evaluator:
    """Fixture providing a fresh Evaluator instance."""
    return Evaluator()


@pytest.fixture
def repl() -> StepCalcREPL:
    """Fixture providing a fresh StepCalcREPL instance."""
    return StepCalcREPL()


# ======================================================================
# 1. Arithmetic & Precedence Tests
# ======================================================================

@pytest.mark.parametrize(
    "expr, expected",
    [
        ("5 + 3", 8),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("20 / 4", 5),
        ("22 / 4", 5),           # Integer truncated division
        ("22 % 4", 2),           # Modulo
        ("2 ^ 3", 8),            # Exponentiation
        ("2 ^ 0", 1),            # Zero exponent
        ("0 ^ 5", 0),
        ("2 + 3 * 4", 14),       # * before +
        ("2 * 3 + 4", 10),
        ("20 - 4 - 2", 14),      # Left-associative subtraction
        ("24 / 4 / 2", 3),       # Left-associative division
        ("2 ^ 3 ^ 2", 512),      # Right-associative exponentiation: 2 ^ (3 ^ 2) = 2 ^ 9
        ("(2 ^ 3) ^ 2", 64),     # Parentheses override right-associativity
        ("(2 + 3) * 4", 20),     # Parentheses override precedence
        ("2 * (3 + 4)", 14),
        ("((2 + 3) * (4 + 1)) / 5", 5),
    ],
)
def test_arithmetic_precedence(parser: Parser, evaluator: Evaluator, expr: str, expected: int) -> None:
    node = parser.parse(expr)
    result = evaluator.evaluate(node)
    assert result == expected


# ======================================================================
# 2. Unary Operators Tests
# ======================================================================

@pytest.mark.parametrize(
    "expr, expected",
    [
        ("-5", -5),
        ("+5", 5),
        ("-(-5)", 5),
        ("-5 + 10", 5),
        ("-(3 + 4) * 2", -14),
        ("2 * -3", -6),
        ("-2 ^ 2", -4),          # Power binds tighter than unary prefix
        ("(-2) ^ 2", 4),
    ],
)
def test_unary_operators(parser: Parser, evaluator: Evaluator, expr: str, expected: int) -> None:
    node = parser.parse(expr)
    result = evaluator.evaluate(node)
    assert result == expected


# ======================================================================
# 3. Variable Assignment and Environment Tests
# ======================================================================

def test_variable_assignment(parser: Parser, evaluator: Evaluator) -> None:
    node1 = parser.parse("x = 15")
    assert evaluator.evaluate(node1) == 15

    node2 = parser.parse("y = x * 2 + 5")
    assert evaluator.evaluate(node2) == 35

    node3 = parser.parse("x = 100")
    assert evaluator.evaluate(node3) == 100

    node4 = parser.parse("x + y")
    assert evaluator.evaluate(node4) == 135


def test_undefined_variable_raises_error(parser: Parser, evaluator: Evaluator) -> None:
    node = parser.parse("unknown_var + 10")
    with pytest.raises(UndefinedVariableError) as exc_info:
        evaluator.evaluate(node)
    assert "Undefined variable 'unknown_var'" in str(exc_info.value)
    assert exc_info.value.hint is not None


# ======================================================================
# 4. Runtime Error Tests (Zero Division, Negative Exponent)
# ======================================================================

def test_division_by_zero(parser: Parser, evaluator: Evaluator) -> None:
    node = parser.parse("10 / 0")
    with pytest.raises(DivisionByZeroError) as exc_info:
        evaluator.evaluate(node)
    assert "Cannot divide by zero" in str(exc_info.value)


def test_modulo_by_zero(parser: Parser, evaluator: Evaluator) -> None:
    node = parser.parse("10 % (5 - 5)")
    with pytest.raises(DivisionByZeroError) as exc_info:
        evaluator.evaluate(node)
    assert "modulo by zero" in str(exc_info.value).lower()


def test_negative_exponent(parser: Parser, evaluator: Evaluator) -> None:
    node = parser.parse("2 ^ -3")
    with pytest.raises(NegativeExponentError) as exc_info:
        evaluator.evaluate(node)
    assert "Negative exponent" in str(exc_info.value)


# ======================================================================
# 5. Format & Syntax Error Tests
# ======================================================================

@pytest.mark.parametrize(
    "bad_syntax",
    [
        "5 + * 2",         # Consecutive operators
        "5 +",             # Incomplete expression
        "(5 + 2",          # Unclosed parenthesis
        "5 + 2)",          # Unmatched closing parenthesis
        "5 5",             # Missing operator between numbers
        "= 10",            # Missing LHS in assignment
        "x =",             # Missing RHS in assignment
    ],
)
def test_syntax_format_errors(parser: Parser, bad_syntax: str) -> None:
    with pytest.raises(SyntaxFormatError) as exc_info:
        parser.parse(bad_syntax)
    diag = exc_info.value.format_diagnostic()
    assert "Error" in diag
    assert "Hint" in diag


def test_lexer_illegal_character(parser: Parser) -> None:
    with pytest.raises(LexerError) as exc_info:
        parser.parse("5 @ 3")
    assert "@" in str(exc_info.value)
    diag = exc_info.value.format_diagnostic()
    assert "^" in diag


# ======================================================================
# 6. Step-by-Step Reduction Tracer Tests
# ======================================================================

def test_step_tracer_reduction(parser: Parser, evaluator: Evaluator) -> None:
    tracer = StepTracer(evaluator)
    node = parser.parse("(2 + 3) * 4")
    steps = tracer.trace(node)

    assert len(steps) >= 2
    assert "5 * 4" in steps[0][0]
    assert steps[-1][0] == "20"


def test_step_tracer_with_variables(parser: Parser, evaluator: Evaluator) -> None:
    evaluator.env.set("a", 10)
    tracer = StepTracer(evaluator)
    node = parser.parse("a + 5")
    steps = tracer.trace(node)

    assert len(steps) == 2
    assert "10 + 5" in steps[0][0]
    assert steps[1][0] == "15"


# ======================================================================
# 7. AST Visualizer Tests
# ======================================================================

def test_ast_visualizer(parser: Parser) -> None:
    node = parser.parse("(x + 2) * 3")
    rendered = ASTVisualizer.render(node)
    assert "BinOp: *" in rendered
    assert "BinOp: +" in rendered
    assert "Variable: x" in rendered
    assert "Number: 2" in rendered
    assert "Number: 3" in rendered


# ======================================================================
# 8. REPL Line Execution & Meta Commands
# ======================================================================

def test_repl_commands(repl: StepCalcREPL) -> None:
    # Assignment
    out1 = repl.run_line("k = 42")
    assert out1 == "  [assigned] k = 42"

    # Evaluation
    out2 = repl.run_line("k + 8")
    assert out2 == "  => 50"

    # Explain command
    out3 = repl.run_line("explain k + 8")
    assert out3 is not None
    assert "Explanation:" in out3
    assert "50" in out3

    # Tree command
    out4 = repl.run_line("tree k + 8")
    assert out4 is not None
    assert "Abstract Syntax Tree:" in out4

    # :vars command
    out5 = repl.run_line(":vars")
    assert out5 is not None
    assert "k = 42" in out5

    # :reset command
    out6 = repl.run_line(":reset")
    assert "[Environment reset" in str(out6)
    out7 = repl.run_line(":vars")
    assert "No variables" in str(out7)

    # :help command
    out8 = repl.run_line(":help")
    assert "StepCalc Syntax Guide:" in str(out8)
