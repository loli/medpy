"""Focused setup.py library selection checks without compiling extensions."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.mark.parametrize("legacy", [False, True])
def test_macos_boost_python_library_selection(legacy):
    source = Path(__file__).resolve().parents[1] / "setup.py"
    tree = ast.parse(source.read_text())
    helper = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "try_find_library"
    )
    selection = next(
        node
        for node in tree.body
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "sys.platform == 'darwin'"
    )
    extension = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "maxflow" for t in node.targets)
    )
    extension_factory = Mock()
    namespace = {
        "sys": SimpleNamespace(
            platform="darwin", version_info=SimpleNamespace(major=3, minor=13)
        ),
        "find_library": Mock(
            side_effect=lambda name: (
                "/usr/local/lib/libboost_python3.dylib"
                if legacy and name == "boost_python3"
                else None
            )
        ),
        "Extension": extension_factory,
    }
    exec(
        compile(
            ast.Module(body=[helper, selection, extension], type_ignores=[]),
            str(source),
            "exec",
        ),
        namespace,
    )

    expected = "boost_python3" if legacy else "boost_python313"
    assert extension_factory.call_args.kwargs["libraries"] == [expected]
