"""Integration tests: SmartView draw() calls _preload_for_draw when tree has the hook.

These tests verify the hook inserted into ``ete4.smartview.draw.draw()``
that bulk-loads lazy node properties before a render frame, eliminating
N individual SQL queries per frame (the "cold frame" problem).

The draw hook checks ``hasattr(tree, '_preload_for_draw')`` — present on
``LazyTree``, absent on plain ``ete4.Tree`` — so a plain tree is a safe no-op.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ete4 = pytest.importorskip("ete4")

from ete4.lazytree import LazyTree  # noqa: E402
from ete4.smartview.draw import draw as smartview_draw  # noqa: E402
from ete4.smartview.layout import Layout  # noqa: E402

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_DRAW_OVERRIDES: dict = {"shape": "rectangular", "node-height-min": 0}


def _make_lazy_tree() -> LazyTree:
    """Return a minimal 3-node LazyTree (root + 2 leaves) with no backing store.

    Returns:
        Root ``LazyTree`` with two leaf children, dist=1.0 each.
    """
    root = LazyTree()
    for name in ("A", "B"):
        child = LazyTree()
        child.name = name
        child.dist = 1.0
        root.add_child(child)
    return root


def _make_layout() -> Layout:
    """Return a minimal Layout that produces a rectangular style.

    Returns:
        A ``Layout`` instance with no custom draw functions.
    """
    return Layout(name="test", cache_size=0)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_preload_hook_called_when_tree_has_preload_method() -> None:
    """SmartView draw() calls tree._preload_for_draw when the method is present.

    This is the critical performance path: without this call, SmartView would
    issue one SQL query per node per frame, causing ~2 s cold-frame latency on
    large trees.  LazyTree provides ``_preload_for_draw``; the hook is duck-typed.
    """
    tree = _make_lazy_tree()

    # LazyTree inherits from Cython Tree — instance attributes are read-only, so
    # we patch at the class level instead.
    with patch.object(LazyTree, "_preload_for_draw") as mock_preload:
        layout = _make_layout()
        list(smartview_draw(tree, layouts=[layout], overrides=_DRAW_OVERRIDES))

    assert mock_preload.called, (
        "_preload_for_draw was not called; the preload hook is missing or broken"
    )


def test_preload_hook_called_at_least_once() -> None:
    """_preload_for_draw is called exactly once per draw() invocation."""
    tree = _make_lazy_tree()

    with patch.object(LazyTree, "_preload_for_draw") as mock_preload:
        layout = _make_layout()
        list(smartview_draw(tree, layouts=[layout], overrides=_DRAW_OVERRIDES))

    assert mock_preload.call_count >= 1


def test_preload_hook_not_called_without_preload_method() -> None:
    """draw() on a plain ete4.Tree (no _preload_for_draw) does not raise.

    A regular ``ete4.Tree`` has no ``_preload_for_draw`` method, so the
    duck-typed hook must be a no-op.
    """
    tree = ete4.Tree()
    for name in ("A", "B"):
        child = ete4.Tree()
        child.name = name
        child.dist = 1.0
        tree.add_child(child)

    layout = _make_layout()
    commands = list(
        smartview_draw(tree, layouts=[layout], overrides=_DRAW_OVERRIDES)
    )
    assert len(commands) > 0
    assert not hasattr(tree, "_preload_for_draw")
