"""Unit tests for BackendContext.

Covers: dirty/deleted tracking, set_eager/set_lazy policy changes,
flush_all(), and flush_node() with a mock store.
"""

from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from ete4.lazy_backend import BackendContext, LazyPropsDict, _force_set_props


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ctx(
    mode: str = "rw",
    lazy_props: frozenset[str] | None = None,
    eager_props: frozenset[str] | None = None,
    node_index: dict | None = None,
) -> BackendContext:
    store = MagicMock()
    store.get_many = MagicMock(return_value={})
    store.set_many = MagicMock()
    store.list_properties = MagicMock(return_value=[])
    store._require_writable = MagicMock()
    conn_mock = MagicMock()
    conn_mock.execute = MagicMock(return_value=conn_mock)
    conn_mock.commit = MagicMock()
    store._require_writable.return_value = conn_mock
    return BackendContext(
        store=store,
        lazy_props=lazy_props or frozenset({"lazy_p"}),
        eager_props=eager_props or frozenset({"eager_p"}),
        mode=mode,  # type: ignore[arg-type]
        node_index=node_index or {},
    )


# ---------------------------------------------------------------------------
# mark_dirty
# ---------------------------------------------------------------------------


def test_mark_dirty_creates_set_lazily() -> None:
    """mark_dirty allocates the set on first call and adds prop."""
    ctx = _make_ctx()
    assert 5 not in ctx.dirty
    ctx.mark_dirty(5, "score")
    assert 5 in ctx.dirty
    assert "score" in ctx.dirty[5]


def test_mark_dirty_accumulates() -> None:
    """mark_dirty accumulates multiple props for the same node."""
    ctx = _make_ctx()
    ctx.mark_dirty(1, "a")
    ctx.mark_dirty(1, "b")
    assert ctx.dirty[1] == {"a", "b"}


def test_mark_dirty_removes_from_deleted() -> None:
    """Setting a previously-deleted prop marks it dirty and clears deletion."""
    ctx = _make_ctx()
    ctx.mark_deleted(3, "foo")
    assert "foo" in ctx.deleted_props.get(3, set())

    ctx.mark_dirty(3, "foo")
    assert "foo" not in ctx.deleted_props.get(3, set())
    assert "foo" in ctx.dirty[3]


# ---------------------------------------------------------------------------
# mark_deleted
# ---------------------------------------------------------------------------


def test_mark_deleted_removes_from_dirty() -> None:
    """Deleting a dirty prop moves it from dirty to deleted_props."""
    ctx = _make_ctx()
    ctx.mark_dirty(2, "bar")
    ctx.mark_deleted(2, "bar")
    assert "bar" not in ctx.dirty.get(2, set())
    assert "bar" in ctx.deleted_props[2]


def test_mark_deleted_creates_set_lazily() -> None:
    """mark_deleted allocates the set on first call."""
    ctx = _make_ctx()
    assert 9 not in ctx.deleted_props
    ctx.mark_deleted(9, "prop")
    assert "prop" in ctx.deleted_props[9]


# ---------------------------------------------------------------------------
# set_eager
# ---------------------------------------------------------------------------


def test_set_eager_updates_frozensets() -> None:
    """set_eager moves props from lazy_props to eager_props."""
    ctx = _make_ctx(
        lazy_props=frozenset({"a", "b"}),
        eager_props=frozenset({"c"}),
    )
    ctx.set_eager(["a"])
    assert "a" in ctx.eager_props
    assert "a" not in ctx.lazy_props


def test_set_eager_triggers_get_many_for_loaded_nodes() -> None:
    """set_eager calls get_many once for all loaded nodes."""
    import ete4

    ete_node = ete4.Tree()
    node_id = 7

    ctx = _make_ctx(
        lazy_props=frozenset({"score"}),
        eager_props=frozenset(),
        node_index={node_id: ete_node},
    )
    ctx.store.get_many = MagicMock(return_value={node_id: {"score": 3.14}})
    ctx.set_eager(["score"])

    ctx.store.get_many.assert_called_once_with([node_id], ["score"])
    # Value should be injected into node's props.
    assert dict.__getitem__(ete_node.props, "score") == 3.14


def test_set_eager_no_op_when_no_loaded_nodes() -> None:
    """set_eager with an empty node_index does not call get_many."""
    ctx = _make_ctx(lazy_props=frozenset({"x"}), node_index={})
    ctx.set_eager(["x"])
    ctx.store.get_many.assert_not_called()


# ---------------------------------------------------------------------------
# flush_all
# ---------------------------------------------------------------------------


def test_flush_all_calls_set_many_once_for_all_dirty_nodes() -> None:
    """flush_all issues a single set_many() for all dirty props across nodes."""
    from ete4.lazy_backend import _force_set_props
    from ete4.lazy_tree import LazyTree

    node1 = LazyTree()
    node1._store_id = 1
    node2 = LazyTree()
    node2._store_id = 2

    ctx = _make_ctx(node_index={1: node1, 2: node2})

    # Install LazyPropsDicts
    lpd1 = LazyPropsDict(1, ctx, {"score": 10.0})
    _force_set_props(node1, lpd1)
    lpd2 = LazyPropsDict(2, ctx, {"score": 20.0})
    _force_set_props(node2, lpd2)

    ctx.mark_dirty(1, "score")
    ctx.mark_dirty(2, "score")

    # Register a dummy property so flush_all doesn't try to add_property.
    ctx.new_prop_samples.clear()
    ctx.store.list_properties = MagicMock(return_value=[])

    # Call flush_all.
    ctx.flush_all()

    # set_many should have been called once.
    assert ctx.store.set_many.call_count == 1
    updates = ctx.store.set_many.call_args[0][0]
    prop_names = {u.prop_name for u in updates}
    node_ids = {u.node_id for u in updates}
    assert prop_names == {"score"}
    assert node_ids == {1, 2}


def test_flush_all_clears_dirty_after_flush() -> None:
    """After flush_all, ctx.dirty is empty."""
    from ete4.lazy_backend import _force_set_props
    from ete4.lazy_tree import LazyTree

    node = LazyTree()
    node._store_id = 1
    ctx = _make_ctx(node_index={1: node})
    lpd = LazyPropsDict(1, ctx, {"score": 1.0})
    _force_set_props(node, lpd)
    ctx.mark_dirty(1, "score")
    ctx.new_prop_samples.clear()
    ctx.store.list_properties = MagicMock(return_value=[])

    ctx.flush_all()

    assert ctx.dirty == {}


def test_flush_all_no_writes_when_nothing_dirty() -> None:
    """flush_all does not call set_many when there are no dirty nodes."""
    ctx = _make_ctx()
    ctx.new_prop_samples.clear()
    ctx.store.list_properties = MagicMock(return_value=[])

    count = ctx.flush_all()

    assert count == 0
    ctx.store.set_many.assert_not_called()
