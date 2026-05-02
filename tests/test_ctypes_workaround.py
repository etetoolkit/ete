"""Unit tests for the ctypes-based ETE4 props guard bypass.

ETE4's Tree (Cython cdef class) enforces ``type(x) is dict`` on ``.props``.
``_force_set_props()`` writes a LazyPropsDict (dict subclass) directly to
the C struct, bypassing this check.  These tests verify the correctness
and safety of that bypass.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import ete4
from ete4.lazy_backend import BackendContext, LazyPropsDict, _force_set_props

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _make_minimal_ctx() -> BackendContext:
    """Return a BackendContext backed by a MagicMock store.

    Returns:
        A minimal ``BackendContext`` suitable for unit-testing the ctypes
        bypass without a real SQLite store.
    """
    store = MagicMock()
    return BackendContext(
        store=store,
        lazy_props=frozenset(),
        eager_props=frozenset(["x"]),
        mode="ro",
        node_index={},
    )


def _node_with_lpd(
    initial: dict | None = None,
) -> tuple[ete4.Tree, LazyPropsDict]:
    """Return an ete4 Tree node with a LazyPropsDict installed via ctypes.

    Args:
        initial: Optional initial dict contents for the LazyPropsDict.

    Returns:
        ``(node, lpd)`` where ``lpd`` is the installed LazyPropsDict.
    """
    ctx = _make_minimal_ctx()
    node = ete4.Tree()
    lpd = LazyPropsDict(node_id=1, ctx=ctx, initial=initial or {})
    _force_set_props(node, lpd)
    return node, lpd


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_force_set_props_identity() -> None:
    """After _force_set_props, node.props IS the exact LazyPropsDict passed in.

    This is the core safety check: the installed object must be IS-identical
    (same Python object identity, not just equality) to what .props returns.
    """
    node, lpd = _node_with_lpd()
    assert node.props is lpd


def test_force_set_props_is_accessible() -> None:
    """Props set in the LazyPropsDict before installation are readable via node.props.

    Verifies that the dict contents survive the ctypes write and are
    accessible through the normal node.props interface.
    """
    node, lpd = _node_with_lpd(initial={"x": 99, "label": "hello"})
    assert node.props["x"] == 99
    assert node.props["label"] == "hello"


def test_force_set_props_type_is_lazy_props_dict() -> None:
    """type(node.props) is LazyPropsDict, not plain dict.

    Cython normally enforces ``type(v) is dict`` on assignment; after the
    ctypes bypass this invariant is deliberately broken.  This test confirms
    the type guard was successfully circumvented.
    """
    node, _ = _node_with_lpd()
    assert type(node.props) is LazyPropsDict


def test_force_set_props_does_not_break_tree() -> None:
    """The tree node remains structurally functional after the ctypes write.

    Verifies: children can be added and traversed, name/dist attributes
    work, and is_leaf/is_root behave as expected.
    """
    node, _ = _node_with_lpd()
    child = ete4.Tree()
    child.name = "leaf"
    child.dist = 1.5

    node.add_child(child)

    assert node.is_root
    assert not node.is_leaf
    assert len(list(node.children)) == 1
    leaf = next(iter(node.children))
    assert leaf.name == "leaf"
    assert leaf.dist == pytest.approx(1.5)
