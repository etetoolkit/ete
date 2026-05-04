"""Unit tests for LazyPropsDict.

Tests cover every dict-protocol override: __getitem__, __setitem__,
__delitem__, __contains__, get(), and flush().  A mock BackendContext
is used so no real TreeStore or SQLite is needed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ete4.lazytree import BackendContext, LazyPropsDict
from etestore.exceptions import ReadOnlyStoreError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_ctx(
    mode: str = "ro",
    lazy_props: frozenset[str] | None = None,
    eager_props: frozenset[str] | None = None,
) -> BackendContext:
    """Build a BackendContext with a mock store."""
    store = MagicMock()
    store.get = MagicMock(return_value=42)
    ctx = BackendContext(
        store=store,
        lazy_props=lazy_props or frozenset({"lazy_prop", "another_lazy"}),
        eager_props=eager_props or frozenset({"eager_prop"}),
        mode=mode,  # type: ignore[arg-type]
        node_index={},
    )
    return ctx


def _make_lpd(
    node_id: int = 1,
    initial: dict | None = None,
    mode: str = "ro",
    lazy_props: frozenset[str] | None = None,
    eager_props: frozenset[str] | None = None,
) -> tuple[LazyPropsDict, BackendContext]:
    ctx = _make_ctx(mode=mode, lazy_props=lazy_props, eager_props=eager_props)
    lpd = LazyPropsDict(node_id, ctx, initial or {})
    return lpd, ctx


# ---------------------------------------------------------------------------
# __getitem__ — eager prop (dict hit)
# ---------------------------------------------------------------------------


def test_getitem_eager_prop_is_dict_hit() -> None:
    """Accessing an eager prop returns its cached dict value without a store call."""
    lpd, ctx = _make_lpd(initial={"eager_prop": "hello"})
    assert lpd["eager_prop"] == "hello"
    ctx.store.get.assert_not_called()


# ---------------------------------------------------------------------------
# __getitem__ — lazy prop (triggers store.get)
# ---------------------------------------------------------------------------


def test_getitem_lazy_prop_fetches_from_store() -> None:
    """Accessing an unknown lazy prop triggers a store.get() call."""
    ctx = _make_ctx()
    ctx.store.get = MagicMock(return_value=99)
    lpd = LazyPropsDict(5, ctx, {})

    val = lpd["lazy_prop"]

    ctx.store.get.assert_called_once_with(5, "lazy_prop")
    assert val == 99


def test_getitem_lazy_prop_caches_after_fetch() -> None:
    """A lazy prop fetched from store is cached in the dict for subsequent reads."""
    ctx = _make_ctx()
    ctx.store.get = MagicMock(return_value=123)
    lpd = LazyPropsDict(3, ctx, {})

    # First access: store hit.
    val1 = lpd["lazy_prop"]
    # Second access: cache hit, store NOT called again.
    val2 = lpd["lazy_prop"]

    assert ctx.store.get.call_count == 1
    assert val1 == val2 == 123


# ---------------------------------------------------------------------------
# __getitem__ — absent sparse prop (KeyError)
# ---------------------------------------------------------------------------


def test_getitem_absent_sparse_prop_raises_key_error() -> None:
    """A lazy prop absent on this node (store raises KeyError) propagates KeyError."""
    ctx = _make_ctx()
    ctx.store.get = MagicMock(side_effect=KeyError("no value"))
    lpd = LazyPropsDict(7, ctx, {})

    with pytest.raises(KeyError):
        _ = lpd["lazy_prop"]


def test_getitem_unknown_prop_raises_key_error() -> None:
    """A prop not in any policy raises KeyError without calling the store."""
    lpd, ctx = _make_lpd()
    with pytest.raises(KeyError):
        _ = lpd["totally_unknown_key"]
    ctx.store.get.assert_not_called()


# ---------------------------------------------------------------------------
# __setitem__ — marks dirty
# ---------------------------------------------------------------------------


def test_setitem_marks_dirty_in_rw_mode() -> None:
    """Setting a prop in rw mode records it in ctx.dirty."""
    lpd, ctx = _make_lpd(
        initial={"eager_prop": "old"},
        mode="rw",
    )
    lpd["eager_prop"] = "new"

    assert 1 in ctx.dirty
    assert "eager_prop" in ctx.dirty[1]
    assert dict.__getitem__(lpd, "eager_prop") == "new"


def test_setitem_raises_in_ro_mode() -> None:
    """Setting a prop in ro mode raises ReadOnlyStoreError."""
    lpd, _ = _make_lpd(initial={"eager_prop": "old"}, mode="ro")
    with pytest.raises(ReadOnlyStoreError):
        lpd["eager_prop"] = "new"


def test_setitem_new_prop_registers_sample() -> None:
    """Setting a brand-new prop registers a sample in ctx.new_prop_samples."""
    lpd, ctx = _make_lpd(mode="rw")
    lpd["brand_new_prop"] = 3.14

    assert "brand_new_prop" in ctx.new_prop_samples
    assert ctx.new_prop_samples["brand_new_prop"] == 3.14


# ---------------------------------------------------------------------------
# __delitem__ — marks deleted
# ---------------------------------------------------------------------------


def test_delitem_marks_deleted() -> None:
    """Deleting a prop in rw mode marks it in ctx.deleted_props."""
    lpd, ctx = _make_lpd(initial={"eager_prop": "value"}, mode="rw")
    del lpd["eager_prop"]

    assert 1 in ctx.deleted_props
    assert "eager_prop" in ctx.deleted_props[1]
    assert "eager_prop" not in dict.keys(lpd)


def test_delitem_raises_in_ro_mode() -> None:
    """Deleting a prop in ro mode raises ReadOnlyStoreError."""
    lpd, _ = _make_lpd(initial={"eager_prop": "value"}, mode="ro")
    with pytest.raises(ReadOnlyStoreError):
        del lpd["eager_prop"]


def test_delitem_absent_prop_raises_key_error() -> None:
    """Deleting a prop not present on this node raises KeyError."""
    ctx = _make_ctx(mode="rw")
    ctx.store.get = MagicMock(side_effect=KeyError("absent"))
    lpd = LazyPropsDict(1, ctx, {})

    with pytest.raises(KeyError):
        del lpd["lazy_prop"]


# ---------------------------------------------------------------------------
# __contains__
# ---------------------------------------------------------------------------


def test_contains_returns_true_for_lazy_prop_even_if_not_loaded() -> None:
    """__contains__ returns True for a lazy prop even before it is fetched."""
    lpd, _ = _make_lpd()
    assert "lazy_prop" in lpd


def test_contains_returns_true_for_eager_prop_in_dict() -> None:
    """__contains__ returns True for an eager prop already in the dict."""
    lpd, _ = _make_lpd(initial={"eager_prop": "x"})
    assert "eager_prop" in lpd


def test_contains_returns_false_for_unknown_prop() -> None:
    """__contains__ returns False for a prop not in any policy."""
    lpd, _ = _make_lpd()
    assert "does_not_exist" not in lpd


def test_contains_returns_true_for_eager_prop_via_frozenset() -> None:
    """__contains__ returns True for an eager prop that is known but not yet set."""
    lpd, _ = _make_lpd()
    # 'eager_prop' is in ctx.eager_props frozenset but not in the dict.
    assert "eager_prop" in lpd


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def test_get_returns_value_when_present() -> None:
    """get() returns the value when the key is present."""
    lpd, _ = _make_lpd(initial={"eager_prop": "found"})
    assert lpd.get("eager_prop") == "found"


def test_get_returns_default_for_absent_prop() -> None:
    """get() returns the default when the key is absent on this node."""
    ctx = _make_ctx()
    ctx.store.get = MagicMock(side_effect=KeyError("absent"))
    lpd = LazyPropsDict(1, ctx, {})
    assert lpd.get("lazy_prop", "default_val") == "default_val"


def test_get_returns_none_by_default() -> None:
    """get() returns None by default for absent props."""
    ctx = _make_ctx()
    ctx.store.get = MagicMock(side_effect=KeyError("absent"))
    lpd = LazyPropsDict(1, ctx, {})
    assert lpd.get("lazy_prop") is None


# ---------------------------------------------------------------------------
# flush()
# ---------------------------------------------------------------------------


def test_flush_calls_ctx_flush_node() -> None:
    """flush() delegates to ctx.flush_node(node_id)."""
    lpd, ctx = _make_lpd(node_id=42, mode="rw")

    # BackendContext uses __slots__, so we patch via the class method.
    with patch.object(type(ctx), "flush_node", return_value=3) as mock_flush:
        result = lpd.flush()
        mock_flush.assert_called_once_with(42)
    assert result == 3
