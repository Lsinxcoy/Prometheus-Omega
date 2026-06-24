"""ASTMutation — E1: Safe code mutation via Python AST.

8 mutation types (all 100% syntax-safe):
1. RENAME — rename variables/functions
2. LOG_ADD — add logging statements
3. ERROR_HANDLE — add try/except blocks
4. TYPE_ANNOTATE — add type annotations
5. EXTRACT_CONST — extract magic numbers to constants
6. SIMPLIFY_COND — simplify nested if/else
7. DOC_ADD — add docstrings
8. ASSERT_ADD — add assertion checks

All mutations use ast.parse + ast.unparse, guaranteeing syntactic validity.
"""
from __future__ import annotations

import ast
import copy
import re

from prometheus_z.schema import ZConfig


class ASTMutation:
    """E1: AST-safe code mutation engine."""

    MUTATION_TYPES = [
        "rename", "log_add", "error_handle", "type_annotate",
        "extract_const", "simplify_cond", "doc_add", "assert_add",
    ]

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._stats = {m: 0 for m in self.MUTATION_TYPES}
        self._stats["failed"] = 0

    def mutate(self, code: str, mutation_type: str = "rename",
               **kwargs) -> str | None:
        """Apply a single mutation to code.

        Returns mutated code, or None if mutation fails (syntax-safe: never returns invalid code).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            self._stats["failed"] += 1
            return None

        try:
            if mutation_type == "rename":
                old_name = kwargs.get("old_name", "x")
                new_name = kwargs.get("new_name", "y")
                tree = self._rename(tree, old_name, new_name)
            elif mutation_type == "log_add":
                tree = self._add_logging(tree)
            elif mutation_type == "error_handle":
                tree = self._add_error_handling(tree)
            elif mutation_type == "extract_const":
                tree = self._extract_constants(tree)
            elif mutation_type == "doc_add":
                tree = self._add_docstrings(tree)
            elif mutation_type == "assert_add":
                tree = self._add_assertions(tree)
            elif mutation_type == "type_annotate":
                tree = self._add_type_annotations(tree)
            elif mutation_type == "simplify_cond":
                tree = self._simplify_conditions(tree)
            else:
                return None

            # Verify the mutation produces valid Python
            result = ast.unparse(tree)
            ast.parse(result)  # Round-trip verify
            self._stats[mutation_type] += 1
            return result

        except Exception:
            self._stats["failed"] += 1
            return None

    def safe_mutate(self, code: str, mutation_type: str = "rename",
                    **kwargs) -> str:
        """Mutate with fallback: if mutation fails, return original code."""
        result = self.mutate(code, mutation_type, **kwargs)
        return result if result is not None else code

    def _rename(self, tree: ast.AST, old_name: str, new_name: str) -> ast.AST:
        """Rename all occurrences of old_name to new_name."""
        tree = copy.deepcopy(tree)
        class Renamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == old_name:
                    node.id = new_name
                return node
            def visit_FunctionDef(self, node):
                if node.name == old_name:
                    node.name = new_name
                self.generic_visit(node)
                return node
            def visit_arg(self, node):
                if node.arg == old_name:
                    node.arg = new_name
                return node
        return Renamer().visit(tree)

    def _add_logging(self, tree: ast.AST) -> ast.AST:
        """Add logging to function entries."""
        tree = copy.deepcopy(tree)
        class LogAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                log_stmt = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="logger", ctx=ast.Load()),
                            attr="info",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Constant(value=f"Entering {node.name}")],
                        keywords=[],
                    )
                )
                node.body.insert(0, log_stmt)
                return node
        return LogAdder().visit(tree)

    def _add_error_handling(self, tree: ast.AST) -> ast.AST:
        """Wrap function bodies in try/except."""
        tree = copy.deepcopy(tree)
        class ErrorHandler(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                original_body = node.body
                try_body = original_body
                except_body = [
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="logger", ctx=ast.Load()),
                                attr="error",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Call(
                                func=ast.Name(id="str", ctx=ast.Load()),
                                args=[ast.Name(id="e", ctx=ast.Load())],
                                keywords=[],
                            )],
                            keywords=[],
                        )
                    )
                ]
                try_node = ast.Try(
                    body=try_body,
                    handlers=[ast.ExceptHandler(
                        type=ast.Name(id="Exception", ctx=ast.Load()),
                        name="e",
                        body=except_body,
                    )],
                    orelse=[],
                    finalbody=[],
                )
                node.body = [try_node]
                return node
        return ErrorHandler().visit(tree)

    def _extract_constants(self, tree: ast.AST) -> ast.AST:
        """Extract magic numbers to named constants."""
        tree = copy.deepcopy(tree)
        class ConstExtractor(ast.NodeTransformer):
            def __init__(self):
                self.constants = {}
                self.counter = 0

            def visit_Constant(self, node):
                if isinstance(node.value, (int, float)) and node.value not in (0, 1, -1, True, False):
                    if node.value not in self.constants:
                        self.counter += 1
                        name = f"CONST_{self.counter}"
                        self.constants[node.value] = name
                    return ast.Name(id=self.constants[node.value], ctx=ast.Load())
                return node
        transformer = ConstExtractor()
        tree = transformer.visit(tree)
        return tree

    def _add_docstrings(self, tree: ast.AST) -> ast.AST:
        """Add docstrings to functions without them."""
        tree = copy.deepcopy(tree)
        class DocAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Check if first statement is a docstring
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    return node  # Already has docstring
                docstring = ast.Expr(value=ast.Constant(value=f"TODO: Document {node.name}"))
                node.body.insert(0, docstring)
                return node
        return DocAdder().visit(tree)

    def _add_assertions(self, tree: ast.AST) -> ast.AST:
        """Add assertions at function entries for argument validation."""
        tree = copy.deepcopy(tree)
        class AssertAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                for arg in node.args.args:
                    assert_stmt = ast.Assert(
                        test=ast.Compare(
                            left=ast.Name(id=arg.arg, ctx=ast.Load()),
                            ops=[ast.IsNot()],
                            comparators=[ast.Constant(value=None)],
                        ),
                        msg=ast.Constant(value=f"{arg.arg} must not be None"),
                    )
                    node.body.insert(0, assert_stmt)
                return node
        return AssertAdder().visit(tree)

    def _add_type_annotations(self, tree: ast.AST) -> ast.AST:
        """Add 'Any' type annotations to untyped function arguments."""
        tree = copy.deepcopy(tree)
        class TypeAnnotator(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                for arg in node.args.args:
                    if arg.annotation is None:
                        arg.annotation = ast.Name(id="Any", ctx=ast.Load())
                return node
        return TypeAnnotator().visit(tree)

    def _simplify_conditions(self, tree: ast.AST) -> ast.AST:
        """Simplify nested if/else patterns.

        Strategy: Flatten `if A: if B: X` → `if A and B: X`.
        Also flatten single-branch else-of-if.
        """
        class Simplifier(ast.NodeTransformer):
            simplified = False

            def visit_If(self, node):
                # First, recursively simplify children
                self.generic_visit(node)

                # Pattern: if A: if B: body → if A and B: body
                if (len(node.body) == 1
                        and isinstance(node.body[0], ast.If)
                        and not node.body[0].orelse):
                    inner = node.body[0]
                    combined_test = ast.BoolOp(
                        op=ast.And(),
                        values=[node.test, inner.test],
                    )
                    ast.copy_location(combined_test, node.test)
                    new_if = ast.If(
                        test=combined_test,
                        body=inner.body,
                        orelse=node.orelse,
                    )
                    ast.copy_location(new_if, node)
                    self.simplified = True
                    return new_if

                # Pattern: if A: X; else: if B: Y → if A: X; elif B: Y
                if (len(node.orelse) == 1
                        and isinstance(node.orelse[0], ast.If)):
                    inner = node.orelse[0]
                    node.orelse = [inner]
                    # Already an elif in practice (ast represents elif as If in orelse)

                return node

        simplifier = Simplifier()
        new_tree = simplifier.visit(tree)
        if simplifier.simplified:
            self._stats["simplifications"] += 1
        return new_tree

    @property
    def stats(self) -> dict:
        return dict(self._stats)
