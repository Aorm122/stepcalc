"""EBNF grammar definition for StepCalc using Lark.

This module provides the formal context-free grammar for the StepCalc language.
By leveraging Lark's LALR(1) parser engine, all tokenization and parsing are handled
declaratively without any naive if-else text processing.
"""

STEPCALC_GRAMMAR = r"""
?start: statement

?statement: assignment
          | explain_cmd
          | tree_cmd
          | expr

assignment: CNAME "=" expr
explain_cmd: "explain" expr
tree_cmd: "tree" expr

?expr: expr "+" term     -> add
     | expr "-" term     -> sub
     | term

?term: term "*" unary    -> mul
     | term "/" unary    -> div
     | term "%" unary    -> mod
     | unary

?unary: "+" unary        -> pos
      | "-" unary        -> neg
      | power

?power: primary "^" unary -> pow
      | primary

?primary: INT            -> number
        | CNAME          -> variable
        | "(" expr ")"

%import common.INT
%import common.CNAME
%import common.WS
%ignore WS

COMMENT: /#[^\n]*/
%ignore COMMENT
"""
