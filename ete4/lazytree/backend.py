"""BackendContext and LazyPropsDict — lazy property loading infrastructure.

``BackendContext`` is shared by all nodes in a single ``LazyTree`` session.
``LazyPropsDict`` is a ``dict`` subclass whose instances are installed on
every tree node (bypassing Cython's type guard via :func:`_force_set_props`).
Property misses trigger a store fetch; writes track dirty state for deferred
flushing.

etestore is an optional dependency of ete4. This module will raise
``ImportError`` at use time (not import time) if etestore is not installed.
"""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING, Any, Literal

_Py_IncRef = ctypes.pythonapi.Py_IncRef
_Py_IncRef.argtypes = [ctypes.py_object]
_Py_IncRef.restype = None

_Py_DecRef = ctypes.pythonapi.Py_DecRef
_Py_DecRef.argtypes = [ctypes.py_object]
_Py_DecRef.restype = None

# Cache the from_address classmethod at module level: avoids one attribute
# lookup per call and is 4× faster than ctypes.cast for the pointer write
# in _force_set_props.
_c_long_from_addr = ctypes.c_long.from_address

from etestore.exceptions import ReadOnlyStoreError, StoreClosedError

if TYPE_CHECKING:
    from ete4.lazytree.tree import LazyTree
    from etestore.api import TreeStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROPS_OFFSET: int | None = None


def _find_props_offset() -> int:
    """Discover the byte offset of the ``props`` field in the Cython Tree struct.

    Runs once and caches the result in ``_PROPS_OFFSET``.

    Returns:
        Byte offset of ``props`` within the Tree C struct.

    Raises:
        RuntimeError: if the offset cannot be found (ete4 ABI changed).
    """
    import ete4

    sentinel: dict[str, Any] = {"_sentinel_": 999}
    node = ete4.Tree()
    node.props = sentinel
    node_addr = id(node)
    sentinel_addr = id(sentinel)
    for offset in range(0, 300, 8):
        try:
            if _c_long_from_addr(node_addr + offset).value == sentinel_addr:
                return offset
        except Exception:
            pass
    raise RuntimeError(
        "Cannot find ete4 Tree.props offset — ete4 ABI may have changed"
    )


def _force_set_props(node: Any, new_dict: dict[str, Any]) -> None:
    """Install ``new_dict`` as ``node.props``, bypassing Cython's type guard.

    Cython declares ``props`` as ``cdef public dict``, which enforces
    ``type(value) is dict``.  We use ctypes to write directly to the C-level
    struct slot, correctly maintaining reference counts via the CPython API.

    Args:
        node: An ete4 ``Tree`` instance.
        new_dict: The ``LazyPropsDict`` (or any dict subclass) to install.
    """
    global _PROPS_OFFSET
    if _PROPS_OFFSET is None:
        _PROPS_OFFSET = _find_props_offset()
    old_dict = node.props  # Python-level read — safe, keeps a reference alive
    _Py_IncRef(new_dict)   # bump before writing pointer — prevent GC window
    _c_long_from_addr(id(node) + _PROPS_OFFSET).value = id(new_dict)
    _Py_DecRef(old_dict)   # drop old ref via typed API — no raw address math


# ---------------------------------------------------------------------------
# BackendContext
# ---------------------------------------------------------------------------

#: DType names whose values are loaded eagerly (scalars and text).
EAGER_DTYPES: frozenset[str] = frozenset(
    {
        "text",
        "int",
        "real",
        "bool",
        "categorical",
        "categorical_interned",
        "sequence",
        "dict",
        "json",
    }
)

#: DType names whose values are loaded on demand (blobs).
LAZY_DTYPES: frozenset[str] = frozenset(
    {"ndarray", "array_float", "array_int", "array_bool_packed", "msgpack"}
)


class BackendContext:
    """Shared state for all nodes in a single ``LazyTree`` session.

    One ``BackendContext`` instance is created by ``LazyTree.open()`` and
    shared via the ``_ctx`` slot on every node.  It holds the store
    reference, the prop policy frozensets, and dirty/deleted tracking
    structures.

    Attributes:
        store: The open ``TreeStore`` session.
        lazy_props: Prop names loaded on demand.
        eager_props: Prop names always kept in memory.
        mode: ``'ro'`` or ``'rw'``.
        dirty: ``{node_id → set of dirty prop names}`` (rw only).
        deleted_props: ``{node_id → set of prop names deleted from this node}``.
        new_prop_samples: ``{name → sample value}`` for props created in-session.
        node_index: ``{store_id → LazyTree node}`` for preload support.
    """

    __slots__ = (
        "store",
        "lazy_props",
        "eager_props",
        "mode",
        "dirty",
        "deleted_props",
        "new_prop_samples",
        "node_index",
        "preload_done",
    )

    def __init__(
        self,
        store: TreeStore,
        lazy_props: frozenset[str],
        eager_props: frozenset[str],
        mode: Literal["ro", "rw"],
        node_index: dict[int, LazyTree],
    ) -> None:
        self.store = store
        self.lazy_props = lazy_props
        self.eager_props = eager_props
        self.mode = mode
        self.dirty: dict[int, set[str]] = {}
        self.deleted_props: dict[int, set[str]] = {}
        self.new_prop_samples: dict[str, Any] = {}
        self.node_index = node_index
        # Props that have been fully bulk-loaded (sparse nodes may still lack
        # the value, but re-querying them would return None again).
        self.preload_done: set[str] = set()

    # ------------------------------------------------------------------
    # dirty tracking
    # ------------------------------------------------------------------

    def mark_dirty(self, node_id: int, prop: str) -> None:
        """Record that ``prop`` on ``node_id`` has been modified in memory.

        Args:
            node_id: Store ID of the modified node.
            prop: Property name that was changed.
        """
        self.dirty.setdefault(node_id, set()).add(prop)
        # If we previously marked it deleted, undo that.
        if node_id in self.deleted_props:
            self.deleted_props[node_id].discard(prop)

    def mark_deleted(self, node_id: int, prop: str) -> None:
        """Record that ``prop`` was deleted from ``node_id``.

        Args:
            node_id: Store ID of the node.
            prop: Property name that was deleted.
        """
        self.deleted_props.setdefault(node_id, set()).add(prop)
        if node_id in self.dirty:
            self.dirty[node_id].discard(prop)

    def register_new_prop(self, name: str, sample: Any) -> None:
        """Record a sample value for a new property not yet in the catalog.

        Args:
            name: New property name.
            sample: A representative value used to infer ``dtype`` on flush.
        """
        if name not in self.new_prop_samples:
            self.new_prop_samples[name] = sample

    # ------------------------------------------------------------------
    # flushing
    # ------------------------------------------------------------------

    def flush_node(self, node_id: int) -> int:
        """Write dirty props for a single node to the store.

        Args:
            node_id: Store ID of the node to flush.

        Returns:
            Number of ``PropertyUpdate`` records written.
        """
        return self._flush_nodes([node_id])

    def flush_all(self) -> int:
        """Write all in-memory dirty props to the store in one transaction.

        Returns:
            Total number of ``PropertyUpdate`` records written.
        """
        return self._flush_nodes(list(self.dirty.keys()))

    def _flush_nodes(self, node_ids: list[int]) -> int:
        """Internal: flush a list of node IDs in one set_many() call.

        Args:
            node_ids: Store IDs to flush.

        Returns:
            Number of updates written.
        """
        from etestore.types import PropertyUpdate

        self._ensure_new_props_registered()
        updates: list[PropertyUpdate] = []
        for nid in node_ids:
            dirty_props = self.dirty.get(nid)
            if not dirty_props:
                continue
            node = self.node_index.get(nid)
            if node is None:
                continue
            for prop in dirty_props:
                val = dict.__getitem__(node.props, prop)
                updates.append(PropertyUpdate(node_id=nid, prop_name=prop, value=val))
        if updates:
            self.store.set_many(updates)
        for nid in node_ids:
            self.dirty.pop(nid, None)
        self._flush_deletions(node_ids)
        return len(updates)

    def _flush_deletions(self, node_ids: list[int]) -> None:
        """Delete props in ``deleted_props`` from the store for ``node_ids``."""
        conn = self.store._require_writable()
        for nid in node_ids:
            props_to_delete = self.deleted_props.get(nid)
            if not props_to_delete:
                continue
            for prop in props_to_delete:
                conn.execute(
                    "DELETE FROM node_property WHERE node_id = ? AND prop_name = ?",
                    (nid, prop),
                )
            self.deleted_props.pop(nid, None)
        conn.commit()

    def _ensure_new_props_registered(self) -> None:
        """Register any new properties (not yet in catalog) before flushing."""
        if not self.new_prop_samples:
            return
        from etestore.types import PropertyInfo, _infer_dtype, _storage_for

        existing = {info.name for info in self.store.list_properties()}
        for name, sample in self.new_prop_samples.items():
            if name in existing:
                continue
            dtype = _infer_dtype(sample)
            info = PropertyInfo(
                name=name,
                dtype=dtype,
                storage_col=_storage_for(dtype),
                interned=(dtype == "categorical_interned"),
            )
            self.store.add_property(info)
            # Update lazy/eager sets.
            if dtype in LAZY_DTYPES:
                self.lazy_props = self.lazy_props | frozenset([name])
            else:
                self.eager_props = self.eager_props | frozenset([name])
        self.new_prop_samples.clear()

    # ------------------------------------------------------------------
    # prop policy updates
    # ------------------------------------------------------------------

    def set_eager(self, props: list[str]) -> None:
        """Promote props to always-in-memory, loading them for loaded nodes.

        Args:
            props: Property names to make eager.
        """
        newly_eager = [p for p in props if p in self.lazy_props]
        self.eager_props = self.eager_props | frozenset(props)
        self.lazy_props = self.lazy_props - frozenset(props)
        if not newly_eager or not self.node_index:
            return
        all_ids = list(self.node_index.keys())
        values = self.store.get_many(all_ids, newly_eager)
        for nid, prop_vals in values.items():
            node = self.node_index.get(nid)
            if node is None:
                continue
            for name, val in prop_vals.items():
                if val is not None:
                    dict.__setitem__(node.props, name, val)

    def set_lazy(self, props: list[str]) -> None:
        """Demote props to on-demand loading, evicting clean cached values.

        Args:
            props: Property names to make lazy.
        """
        self.lazy_props = self.lazy_props | frozenset(props)
        self.eager_props = self.eager_props - frozenset(props)
        for nid, node in self.node_index.items():
            dirty_for_node = self.dirty.get(nid, set())
            for prop in props:
                if prop not in dirty_for_node:
                    dict.pop(node.props, prop, None)


# ---------------------------------------------------------------------------
# LazyPropsDict
# ---------------------------------------------------------------------------


class LazyPropsDict(dict[str, Any]):
    """A ``dict`` subclass that loads missing properties from the store on demand.

    Installed on every node in a ``LazyTree`` session via
    :func:`_force_set_props`.  Eager props are pre-loaded into the underlying
    dict.  Lazy props trigger a store fetch on first access and are cached
    for subsequent reads.

    Args:
        node_id: Store ID of the tree node this dict belongs to.
        ctx: Shared ``BackendContext`` for the session.
        initial: Initial dict contents (eager props already loaded).
    """

    __slots__ = ("_node_id", "_ctx", "_missing")

    def __init__(
        self,
        node_id: int,
        ctx: BackendContext,
        initial: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(initial or {})
        self._node_id = node_id
        self._ctx = ctx
        # Keys confirmed absent from the store for this node — avoids re-querying
        # sparse props (e.g. leaf-only arrays) on internal nodes every frame.
        self._missing: set[str] = set()

    # ------------------------------------------------------------------
    # dict protocol overrides
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        """Return the value for ``key``, fetching from store if lazy and not cached.

        Args:
            key: Property name.

        Returns:
            The decoded property value.

        Raises:
            KeyError: if the prop does not exist on this node.
            StoreClosedError: if the backing store has been closed.
        """
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        if self._ctx is None:
            raise StoreClosedError("store is closed")
        if key in self._missing:
            raise KeyError(key)
        if key not in self._ctx.lazy_props:
            raise KeyError(key)
        # Fetch from store.
        try:
            val = self._ctx.store.get(self._node_id, key)
        except KeyError:
            # Sparse node: record absence so subsequent frames skip the SQL query.
            self._missing.add(key)
            raise KeyError(key) from None
        # Cache in dict.
        dict.__setitem__(self, key, val)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        """Set ``key`` to ``value``, tracking the change as dirty.

        Args:
            key: Property name.
            value: New value.

        Raises:
            ReadOnlyStoreError: if the store is read-only.
        """
        if self._ctx.mode == "ro":
            raise ReadOnlyStoreError(
                f"cannot set prop {key!r}: store is read-only"
            )
        is_new = key not in self._ctx.lazy_props and key not in self._ctx.eager_props
        dict.__setitem__(self, key, value)
        self._missing.discard(key)
        self._ctx.mark_dirty(self._node_id, key)
        if is_new:
            self._ctx.register_new_prop(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete ``key`` from this node's props, marking it for removal in DB.

        Args:
            key: Property name.

        Raises:
            ReadOnlyStoreError: if the store is read-only.
            KeyError: if key is not present on this node.
        """
        if self._ctx.mode == "ro":
            raise ReadOnlyStoreError(
                f"cannot delete prop {key!r}: store is read-only"
            )
        if not dict.__contains__(self, key):
            # Try loading from store first to confirm existence.
            try:
                self.__getitem__(key)
            except KeyError:
                raise KeyError(key) from None
        dict.__delitem__(self, key)
        self._ctx.mark_deleted(self._node_id, key)

    def __contains__(self, key: object) -> bool:
        """Return ``True`` if ``key`` is in dict or is a known lazy/eager prop.

        Args:
            key: Property name.

        Returns:
            ``True`` if the property is present or potentially present.
        """
        if dict.__contains__(self, key):
            return True
        if not isinstance(key, str):
            return False
        if key in self._missing:
            return False
        return key in self._ctx.lazy_props or key in self._ctx.eager_props

    def get(
        self, key: str, default: Any = None  # type: ignore[override]
    ) -> Any:
        """Return value for ``key``, or ``default`` if absent.

        Args:
            key: Property name.
            default: Value to return when the key is not found.

        Returns:
            The property value, or ``default``.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def flush(self) -> int:
        """Write this node's dirty props to the store.

        Returns:
            Number of ``PropertyUpdate`` records written.
        """
        return self._ctx.flush_node(self._node_id)


__all__ = [
    "BackendContext",
    "LazyPropsDict",
    "EAGER_DTYPES",
    "LAZY_DTYPES",
    "_force_set_props",
]
