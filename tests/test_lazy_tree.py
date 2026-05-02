"""Integration tests for LazyTree.

All tests use real ``.ete`` files on disk (no mocking of SQLite).
Covers: open, eager/lazy split, lazy prop access, preload, flush,
evict, ReadOnlyStoreError, tree.save(), and LazyTree.info().
"""

from __future__ import annotations

from pathlib import Path

import pytest

ete4 = pytest.importorskip("ete4")
np = pytest.importorskip("numpy")

from ete4.lazy_backend import LazyPropsDict  # noqa: E402
from ete4.lazy_tree import LazyTree  # noqa: E402
from etestore import ReadOnlyStoreError, TreeStore  # noqa: E402
from etestore.io.ete4 import from_ete4, to_ete4  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_test_tree(*, with_arrays: bool = True) -> "ete4.Tree":
    """Return a small 3-node test tree (root + 2 leaves)."""
    root = ete4.Tree()
    root.dist = 0.0
    a = ete4.Tree()
    a.name = "A"
    a.dist = 0.5
    b = ete4.Tree()
    b.name = "B"
    b.dist = 0.3
    root.add_child(a)
    root.add_child(b)
    root.add_prop("score", 1.0)
    a.add_prop("score", 2.5)
    b.add_prop("score", 4.0)
    a.add_prop("label", "alpha")
    b.add_prop("label", "beta")
    if with_arrays:
        a.add_prop("embed", np.array([1.0, 2.0, 3.0], dtype="float64"))
        b.add_prop("embed", np.array([4.0, 5.0, 6.0], dtype="float64"))
    return root


def _leaf(lt: "LazyTree", name: str) -> "LazyTree":
    return next(n for n in lt.traverse() if n.name == name)


# ---------------------------------------------------------------------------
# LazyTree.open — topology + eager props
# ---------------------------------------------------------------------------


def test_open_loads_topology(tmp_path: Path) -> None:
    """LazyTree.open() reconstructs the full tree topology."""
    src = _build_test_tree()
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        node_count = sum(1 for _ in lt.traverse())
        leaf_count = sum(1 for n in lt.traverse() if n.is_leaf)
        assert node_count == 3
        assert leaf_count == 2
    finally:
        lt.store.close()


def test_open_loads_eager_props(tmp_path: Path) -> None:
    """Scalar (eager) props are pre-loaded at open time."""
    src = _build_test_tree()
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        a = _leaf(lt, "A")
        # score is a scalar (real) → eager → pre-loaded in the dict.
        assert dict.__contains__(a.props, "score")
        assert abs(a.props["score"] - 2.5) < 1e-9
    finally:
        lt.store.close()


def test_open_does_not_preload_lazy_props(tmp_path: Path) -> None:
    """Blob (lazy) props are NOT pre-loaded at open time."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        a = _leaf(lt, "A")
        # embed is array_float → lazy → not in dict yet.
        assert not dict.__contains__(a.props, "embed")
        # But __contains__ reports True because ctx.lazy_props knows about it.
        assert "embed" in a.props
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# Lazy prop access triggers store.get
# ---------------------------------------------------------------------------


def test_lazy_prop_access_fetches_from_store(tmp_path: Path) -> None:
    """Accessing a lazy prop for the first time fetches it from the store."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        a = _leaf(lt, "A")
        # Not loaded yet.
        assert not dict.__contains__(a.props, "embed")
        # Access triggers fetch.
        embed = a.props["embed"]
        assert np.allclose(embed, [1.0, 2.0, 3.0])
        # Now cached.
        assert dict.__contains__(a.props, "embed")
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# preload() makes subsequent access a cache hit
# ---------------------------------------------------------------------------


def test_preload_makes_lazy_prop_a_cache_hit(tmp_path: Path) -> None:
    """After preload(), accessing a lazy prop does not query the store."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        a = _leaf(lt, "A")
        a_id = a._store_id
        assert not dict.__contains__(a.props, "embed")

        # Preload for this node only.
        lt.preload([a_id], ["embed"])
        assert dict.__contains__(a.props, "embed")

        # Value is correct.
        assert np.allclose(a.props["embed"], [1.0, 2.0, 3.0])
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# lt.flush() writes dirty props to DB
# ---------------------------------------------------------------------------


def test_flush_writes_dirty_props_to_db(tmp_path: Path) -> None:
    """lt.flush() persists dirty prop changes; reopening reads the new value."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete", mode="rw")
    try:
        a = _leaf(lt, "A")
        a.props["score"] = 99.0
        count = lt.flush()
        assert count >= 1
    finally:
        lt.store.close()

    # Reopen and verify.
    lt2 = LazyTree.open(tmp_path / "t.ete")
    try:
        a2 = _leaf(lt2, "A")
        assert abs(a2.props["score"] - 99.0) < 1e-9
    finally:
        lt2.store.close()


# ---------------------------------------------------------------------------
# lt.evict() removes non-dirty cached props
# ---------------------------------------------------------------------------


def test_evict_removes_non_dirty_cached_props(tmp_path: Path) -> None:
    """evict() removes clean cached lazy props from node dicts."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        a = _leaf(lt, "A")
        # Trigger cache load.
        _ = a.props["embed"]
        assert dict.__contains__(a.props, "embed")

        # Evict all.
        lt.evict()
        assert not dict.__contains__(a.props, "embed")
    finally:
        lt.store.close()


def test_evict_does_not_remove_dirty_props(tmp_path: Path) -> None:
    """evict() does NOT remove dirty (modified but unflushed) props."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete", mode="rw")
    try:
        a = _leaf(lt, "A")
        # Load and mark dirty.
        _ = a.props["embed"]
        a.props["embed"] = np.array([9.0, 9.0, 9.0])

        # Evict should not remove the dirty value.
        lt.evict()
        assert dict.__contains__(a.props, "embed")
        assert np.allclose(a.props["embed"], [9.0, 9.0, 9.0])
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# ReadOnlyStoreError raised on write in ro mode
# ---------------------------------------------------------------------------


def test_readonly_error_on_write(tmp_path: Path) -> None:
    """Attempting to set a prop on a ro-mode LazyTree raises ReadOnlyStoreError."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete", mode="ro")
    try:
        a = _leaf(lt, "A")
        with pytest.raises(ReadOnlyStoreError):
            a.props["score"] = 0.0
    finally:
        lt.store.close()


def test_readonly_error_on_delete(tmp_path: Path) -> None:
    """Attempting to delete a prop on a ro-mode LazyTree raises ReadOnlyStoreError."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete", mode="ro")
    try:
        a = _leaf(lt, "A")
        with pytest.raises(ReadOnlyStoreError):
            del a.props["score"]
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# tree.save() creates a valid new .ete file
# ---------------------------------------------------------------------------


def test_save_creates_valid_ete_file(tmp_path: Path) -> None:
    """save() produces a new .ete file that can be opened with TreeStore."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "src.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "src.ete")
    try:
        lt.save(tmp_path / "copy.ete")
    finally:
        lt.store.close()

    assert (tmp_path / "copy.ete").exists()
    with TreeStore(tmp_path / "copy.ete") as s:
        assert s.node_count() == 3
        assert s.leaf_count() == 2
        props = {p.name for p in s.list_properties()}
        assert "score" in props
        assert "label" in props


def test_save_preserves_prop_values(tmp_path: Path) -> None:
    """save() preserves all eager prop values in the new file."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "src.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "src.ete")
    try:
        lt.save(tmp_path / "copy.ete")
    finally:
        lt.store.close()

    with TreeStore(tmp_path / "copy.ete") as s:
        t_back = to_ete4(s)
    a_back = next(n for n in t_back.traverse() if n.name == "A")
    assert a_back.props.get("label") == "alpha"
    assert abs(a_back.props["score"] - 2.5) < 1e-9


def test_save_raises_if_file_exists(tmp_path: Path) -> None:
    """save() raises FileExistsError when target exists and overwrite=False."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "src.ete")
    store.close()

    (tmp_path / "copy.ete").touch()

    lt = LazyTree.open(tmp_path / "src.ete")
    try:
        with pytest.raises(FileExistsError):
            lt.save(tmp_path / "copy.ete", overwrite=False)
    finally:
        lt.store.close()


# ---------------------------------------------------------------------------
# lt.info() returns non-empty dict with lazy_mode
# ---------------------------------------------------------------------------


def test_lazy_tree_info_returns_dict(tmp_path: Path) -> None:
    """lt.info() returns a dict with node/property details and lazy_mode."""
    src = _build_test_tree(with_arrays=False)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete")
    try:
        info = lt.info()
        assert isinstance(info, dict)
        assert info["node_count"] > 0
        assert any(p["name"] == "score" for p in info["properties"])
    finally:
        lt.store.close()


def test_lazy_tree_info_shows_lazy_mode(tmp_path: Path) -> None:
    """lt.info() includes lazy_mode sub-dict when a LazyTree is open."""
    src = _build_test_tree(with_arrays=True)
    store = from_ete4(src, tmp_path / "t.ete")
    store.close()

    lt = LazyTree.open(tmp_path / "t.ete", mode="rw")
    try:
        info = lt.info()
        assert "lazy_mode" in info
        assert info["lazy_mode"]["mode"] == "rw"
    finally:
        lt.store.close()
