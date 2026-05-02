"""LazyTree — an ete4.Tree backed by an etestore .ete file.

Property reads and writes are mediated by a ``LazyPropsDict`` installed
on every node.  Eager props are loaded in a single ``store.get_many()``
call on open; lazy (blob) props are fetched from the DB only when first
accessed.

Structural changes (add/remove nodes, reroot) happen in the ete4 Tree
in memory and are flushed with :meth:`LazyTree.flush_topology`.

etestore is an optional dependency of ete4; this module raises
``ImportError`` at use time if etestore is not installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from ete4.lazy_backend import (
    EAGER_DTYPES,
    LAZY_DTYPES,
    BackendContext,
    LazyPropsDict,
    _force_set_props,
)

try:
    import ete4 as _ete4_mod

    _ETE4_TREE = _ete4_mod.Tree
except ImportError as _e:  # pragma: no cover
    raise ModuleNotFoundError(
        "ete4 is required for LazyTree; install with `pip install ete4`"
    ) from _e


class LazyTree(_ETE4_TREE):  # type: ignore[misc, valid-type]
    """An ete4 ``Tree`` whose properties are backed by an etestore file.

    Eager props (scalars, text) are loaded into memory at open time.
    Lazy props (blobs/arrays) are fetched on first access.

    Do not construct directly; use :meth:`open`.

    Args:
        (no public constructor — use ``LazyTree.open()``)
    """

    __slots__ = ("_store", "_store_id")

    # ------------------------------------------------------------------
    # constructor
    # ------------------------------------------------------------------

    def __init__(self, data: Any = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        # Will be assigned by LazyTree.open(); None until then.
        self._store: Any = None
        self._store_id: int = -1

    # ------------------------------------------------------------------
    # factory
    # ------------------------------------------------------------------

    @classmethod
    def open(
        cls,
        path: str | Path,
        mode: Literal["ro", "rw"] = "ro",
        eager_props: list[str] | None = None,
        lazy_props: list[str] | None = None,
    ) -> LazyTree:
        """Open an etestore `.ete` file as a ``LazyTree``.

        Loads the full topology and all eager props into memory.
        Lazy (blob) props are deferred until first access.

        Args:
            path: Path to the ``.ete`` file.
            mode: ``'ro'`` for read-only (default) or ``'rw'`` for read-write.
            eager_props: Override which props are eager. When ``None``, all
                scalar/text dtypes are eager; blob dtypes are lazy.
            lazy_props: Override which props are lazy. When ``None``, all
                blob dtypes are lazy.

        Returns:
            Root ``LazyTree`` node with all eager props loaded.

        Raises:
            FileNotFoundError: if ``path`` does not exist.
            ValueError: if ``mode`` is not ``'ro'`` or ``'rw'``.
        """
        if mode not in ("ro", "rw"):
            raise ValueError(f"mode must be 'ro' or 'rw', got {mode!r}")
        ts_mode = "r" if mode == "ro" else "rw"

        from etestore.api import TreeStore

        store = TreeStore(path, mode=ts_mode)
        return cls._build_from_store(store, mode, eager_props, lazy_props)

    # ------------------------------------------------------------------
    # store property
    # ------------------------------------------------------------------

    @property
    def store(self) -> Any:
        """The backing ``TreeStore`` session."""
        return self._store

    # ------------------------------------------------------------------
    # persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path, overwrite: bool = False) -> None:
        """Write current in-memory state to a new ``.ete`` file.

        Flushes all dirty props first, then exports the full tree to
        a new path via ``from_ete4``.

        Args:
            path: Destination path.
            overwrite: Replace the file if it already exists.

        Raises:
            FileExistsError: if ``path`` exists and ``overwrite`` is ``False``.
        """
        from etestore.io.ete4 import from_ete4

        # Make sure all dirty writes are in the source store first.
        if self._store is not None:
            ctx = _get_ctx(self)
            if ctx is not None and ctx.mode == "rw":
                ctx.flush_all()
        from_ete4(self, path, overwrite=overwrite).close()

    def flush(self) -> int:
        """Write all dirty props to the DB.

        Returns:
            Total number of ``PropertyUpdate`` records written.

        Raises:
            PermissionError: if the store is read-only.
        """
        ctx = _get_ctx(self)
        if ctx is None:
            return 0
        if ctx.mode == "ro":
            from etestore.exceptions import ReadOnlyStoreError
            raise ReadOnlyStoreError("cannot flush: store is read-only")
        return ctx.flush_all()

    def flush_topology(self) -> None:
        """Sync in-memory tree topology to the DB.

        Recomputes MPTT (lft/rgt/depth), assigns new IDs to nodes
        added since open, and deletes nodes that were removed.

        Raises:
            PermissionError: if the store is read-only.
        """
        ctx = _get_ctx(self)
        if ctx is None:
            return
        if ctx.mode == "ro":
            from etestore.exceptions import ReadOnlyStoreError
            raise ReadOnlyStoreError("cannot flush_topology: store is read-only")
        conn = ctx.store._require_writable()
        root = _find_root(ctx.node_index)
        if root is None:
            return
        _sync_topology(conn, root, ctx)

    def preload(
        self,
        node_ids: list[int],
        props: list[str] | None = None,
    ) -> None:
        """Bulk-load props for the given node IDs into their LazyPropsDicts.

        Issues a single ``get_many()`` call and writes results directly
        into each node's ``props`` dict without marking them dirty.

        Args:
            node_ids: Store IDs of nodes to preload.
            props: Property names to load.  When ``None``, loads all lazy props.
        """
        ctx = _get_ctx(self)
        if ctx is None or not node_ids:
            return
        _preload_nodes(ctx, node_ids, props)

    def preload_all(self, props: list[str] | None = None) -> None:
        """Preload lazy props for every node currently in memory.

        Args:
            props: Property names to load. When ``None``, loads all lazy props.
        """
        ctx = _get_ctx(self)
        if ctx is None:
            return
        _preload_nodes(ctx, list(ctx.node_index.keys()), props)

    def evict(
        self,
        node_ids: list[int] | None = None,
        props: list[str] | None = None,
    ) -> None:
        """Release cached lazy props from memory (only if not dirty).

        Args:
            node_ids: Nodes to evict from.  When ``None``, all loaded nodes.
            props: Props to evict.  When ``None``, all lazy props.
        """
        ctx = _get_ctx(self)
        if ctx is None:
            return
        target_ids = node_ids if node_ids is not None else list(ctx.node_index.keys())
        target_props = list(props if props is not None else ctx.lazy_props)
        for nid in target_ids:
            node = ctx.node_index.get(nid)
            if node is None:
                continue
            dirty_for_node = ctx.dirty.get(nid, set())
            for prop in target_props:
                if prop not in dirty_for_node:
                    dict.pop(node.props, prop, None)

    def set_eager(self, props: list[str]) -> None:
        """Promote props to eager (always in memory).

        Args:
            props: Property names to promote to eager loading.
        """
        ctx = _get_ctx(self)
        if ctx is not None:
            ctx.set_eager(props)

    def set_lazy(self, props: list[str]) -> None:
        """Demote props to lazy (load on demand).

        Args:
            props: Property names to demote to lazy loading.
        """
        ctx = _get_ctx(self)
        if ctx is not None:
            ctx.set_lazy(props)

    def info(self) -> dict[str, Any]:
        """Return a dict describing store state and lazy session.

        Returns:
            Dict with keys: schema_version, path, node_count, leaf_count,
            properties, and lazy_mode (mode, dirty_props, cached_lazy).
        """
        store = self._store
        if store is None:
            return {}
        ctx = _get_ctx(self)
        result: dict[str, Any] = {
            "schema_version": store.schema_version,
            "path": str(store.path),
            "node_count": store.node_count(),
            "leaf_count": store.leaf_count(),
            "properties": [
                {"name": i.name, "dtype": i.dtype, "storage_col": i.storage_col}
                for i in store.list_properties()
            ],
        }
        if ctx is not None:
            n_dirty = sum(len(v) for v in ctx.dirty.values())
            n_cached = sum(
                sum(1 for k in node.props if k in ctx.lazy_props)
                for node in ctx.node_index.values()
            )
            result["lazy_mode"] = {
                "mode": ctx.mode,
                "dirty_props": n_dirty,
                "cached_lazy": n_cached,
            }
        return result

    # ------------------------------------------------------------------
    # SmartView hook
    # ------------------------------------------------------------------

    def _preload_for_draw(
        self,
        viewport: Any,
        needed_props: list[str] | None = None,
    ) -> None:
        """Best-effort preload called by SmartView before drawing a frame.

        Uses MPTT to identify likely-visible nodes within the viewport
        depth range, then bulk-loads ``needed_props`` for those nodes.
        When ``viewport`` is ``None``, preloads all loaded nodes.

        Args:
            viewport: Viewport hint (may be ``None`` to preload all).
            needed_props: Prop names to load.  Defaults to all lazy props.
        """
        ctx = _get_ctx(self)
        if ctx is None:
            return
        if viewport is None:
            _preload_nodes(ctx, list(ctx.node_index.keys()), needed_props)
            return
        try:
            min_depth = int(viewport.get("min_depth", 0))
            max_depth = int(viewport.get("max_depth", 9999))
        except (AttributeError, TypeError, ValueError):
            _preload_nodes(ctx, list(ctx.node_index.keys()), needed_props)
            return
        conn = ctx.store._require_conn()
        rows = conn.execute(
            "SELECT id FROM node WHERE depth BETWEEN ? AND ?",
            (min_depth, max_depth),
        ).fetchall()
        ids_in_view = [int(r[0]) for r in rows if int(r[0]) in ctx.node_index]
        _preload_nodes(ctx, ids_in_view, needed_props)

    # ------------------------------------------------------------------
    # internal builder
    # ------------------------------------------------------------------

    @classmethod
    def _build_from_store(
        cls,
        store: Any,
        mode: Literal["ro", "rw"],
        eager_props_override: list[str] | None,
        lazy_props_override: list[str] | None,
    ) -> LazyTree:
        """Build a LazyTree from an open TreeStore.

        Args:
            store: Open ``TreeStore``.
            mode: ``'ro'`` or ``'rw'``.
            eager_props_override: Explicit eager prop list or ``None``.
            lazy_props_override: Explicit lazy prop list or ``None``.

        Returns:
            Root ``LazyTree`` node.
        """
        prop_infos = store.list_properties()
        eager_set, lazy_set = _partition_props(
            prop_infos, eager_props_override, lazy_props_override
        )
        topology = store.topology()
        _, ete_nodes = _build_lazy_topology_with_index(topology, cls)
        node_index = _link_nodes_to_store(ete_nodes, store)
        ctx = BackendContext(
            store=store,
            lazy_props=lazy_set,
            eager_props=eager_set,
            mode=mode,
            node_index=node_index,
        )
        store._ctx = ctx
        _install_lazy_dicts(node_index, ctx)
        _prefetch_eager_props(store, node_index, eager_set)
        return node_index[topology.root.id]


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _get_ctx(root: LazyTree) -> BackendContext | None:
    """Return the ``BackendContext`` from a ``LazyTree`` node.

    Args:
        root: A ``LazyTree`` node (any node works).

    Returns:
        The ``BackendContext``, or ``None`` if props are not lazy.
    """
    if isinstance(root.props, LazyPropsDict):
        return root.props._ctx
    return None


def _preload_nodes(
    ctx: BackendContext,
    node_ids: list[int],
    props: list[str] | None = None,
) -> None:
    """Bulk-load props into LazyPropsDicts for the given node IDs.

    Args:
        ctx: Active ``BackendContext``.
        node_ids: Store IDs of nodes to preload.
        props: Prop names to load.  When ``None``, loads all lazy props.
    """
    prop_names = list(props if props is not None else ctx.lazy_props)
    if not prop_names or not node_ids:
        return
    values = ctx.store.get_many(node_ids, prop_names)
    for nid, prop_vals in values.items():
        node = ctx.node_index.get(nid)
        if node is None:
            continue
        for name, val in prop_vals.items():
            if val is not None:
                dict.__setitem__(node.props, name, val)


def _link_nodes_to_store(
    ete_nodes: dict[int, Any],
    store: Any,
) -> dict[int, LazyTree]:
    """Assign store IDs to nodes and build the node_index mapping.

    Args:
        ete_nodes: Node ID → LazyTree node from topology building.
        store: The open TreeStore instance.

    Returns:
        Dict mapping store_id → LazyTree node.
    """
    node_index: dict[int, LazyTree] = {}
    for nid, node in ete_nodes.items():
        node._store = store
        node._store_id = nid
        node_index[nid] = node
    return node_index


def _install_lazy_dicts(
    node_index: dict[int, LazyTree],
    ctx: BackendContext,
) -> None:
    """Install a LazyPropsDict on every node via ctypes bypass.

    Args:
        node_index: All nodes to instrument.
        ctx: Shared BackendContext for this session.
    """
    for nid, node in node_index.items():
        lpd = LazyPropsDict(nid, ctx, dict(node.props))
        _force_set_props(node, lpd)


def _prefetch_eager_props(
    store: Any,
    node_index: dict[int, LazyTree],
    eager_set: frozenset[str],
) -> None:
    """Bulk-load all eager props into node LazyPropsDicts.

    Issues a single get_many() call for all nodes and all eager props.

    Args:
        store: Open TreeStore to fetch from.
        node_index: All loaded nodes.
        eager_set: Property names to pre-populate.
    """
    if not eager_set or not node_index:
        return
    values = store.get_many(list(node_index.keys()), list(eager_set))
    for nid, prop_vals in values.items():
        node_obj = node_index.get(nid)
        if node_obj is None:
            continue
        for name, val in prop_vals.items():
            if val is not None:
                dict.__setitem__(node_obj.props, name, val)


def _partition_props(
    prop_infos: list[Any],
    eager_override: list[str] | None,
    lazy_override: list[str] | None,
) -> tuple[frozenset[str], frozenset[str]]:
    """Split prop names into eager and lazy frozensets.

    Args:
        prop_infos: List of ``PropertyInfo`` from the store.
        eager_override: If given, force exactly these names to be eager.
        lazy_override: If given, force exactly these names to be lazy.

    Returns:
        ``(eager_frozenset, lazy_frozenset)``
    """
    if eager_override is not None:
        eager_set = frozenset(eager_override)
        lazy_set = frozenset(
            i.name for i in prop_infos if i.name not in eager_set
        )
        return eager_set, lazy_set
    if lazy_override is not None:
        lazy_set = frozenset(lazy_override)
        eager_set = frozenset(
            i.name for i in prop_infos if i.name not in lazy_set
        )
        return eager_set, lazy_set
    # Default: dtype-based split.
    eager_set = frozenset(i.name for i in prop_infos if i.dtype in EAGER_DTYPES)
    lazy_set = frozenset(i.name for i in prop_infos if i.dtype in LAZY_DTYPES)
    return eager_set, lazy_set


def _build_lazy_topology_with_index(
    topology: Any,
    tree_cls: type,
) -> tuple[LazyTree, dict[int, LazyTree]]:
    """Build LazyTree nodes from a ``TreeTopology``, returning root and index.

    Args:
        topology: ``TreeTopology`` from the store.
        tree_cls: Node class to instantiate (a ``LazyTree`` subclass).

    Returns:
        ``(root_node, {nid: node})`` mapping.
    """
    nodes: dict[int, Any] = {}
    for nid, ts_node in topology.node_index.items():
        ete_node = tree_cls()
        if ts_node.name is not None:
            ete_node.name = ts_node.name
        if ts_node.dist is not None:
            ete_node.dist = ts_node.dist
        if ts_node.support is not None:
            ete_node.support = ts_node.support
        nodes[nid] = ete_node
    for nid, ts_node in topology.node_index.items():
        for child in ts_node.children:
            nodes[nid].add_child(nodes[child.id])
    root = nodes[topology.root.id]
    return root, nodes


def _find_root(node_index: dict[int, Any]) -> Any | None:
    """Find the root node from a node_index (the one with no ete4 parent).

    Args:
        node_index: Mapping of store_id → LazyTree node.

    Returns:
        Root node, or ``None`` if node_index is empty.
    """
    for node in node_index.values():
        if node.up is None:
            return node
    return None


def _collect_in_memory(
    root: Any,
) -> tuple[dict[int, Any], list[Any]]:
    """Walk root in preorder, partitioning into known and new nodes.

    Args:
        root: Root LazyTree node.

    Returns:
        ``(in_memory, new_nodes)`` where in_memory maps store_id → node
        and new_nodes contains nodes with _store_id == -1.
    """
    in_memory: dict[int, Any] = {}
    new_nodes: list[Any] = []
    for node in root.traverse("preorder"):
        nid: int = node._store_id
        if nid == -1:
            new_nodes.append(node)
        else:
            in_memory[nid] = node
    return in_memory, new_nodes


def _assign_new_node_ids(
    conn: Any,
    ctx: BackendContext,
    in_memory: dict[int, Any],
    new_nodes: list[Any],
) -> None:
    """Assign monotonically-increasing store IDs to newly-created nodes.

    Args:
        conn: Writable SQLite connection.
        ctx: Active BackendContext (node_index updated in place).
        in_memory: Already-known nodes (updated in place with new entries).
        new_nodes: Nodes that need new IDs.
    """
    if not new_nodes:
        return
    row = conn.execute("SELECT COALESCE(MAX(id), -1) + 1 FROM node").fetchone()
    next_id = int(row[0])
    for node in new_nodes:
        node._store_id = next_id
        in_memory[next_id] = node
        ctx.node_index[next_id] = node
        next_id += 1


def _delete_removed_nodes(
    conn: Any,
    ctx: BackendContext,
    in_memory: dict[int, Any],
) -> None:
    """Delete DB rows for nodes that no longer exist in the in-memory tree.

    Args:
        conn: Writable SQLite connection.
        ctx: Active BackendContext (node_index pruned in place).
        in_memory: Current set of live in-memory nodes.
    """
    db_ids = {int(r[0]) for r in conn.execute("SELECT id FROM node").fetchall()}
    ids_to_delete = db_ids - set(in_memory.keys())
    if not ids_to_delete:
        return
    ph = ",".join(["?"] * len(ids_to_delete))
    id_list = list(ids_to_delete)
    conn.execute(f"DELETE FROM node_property WHERE node_id IN ({ph})", id_list)
    conn.execute(f"DELETE FROM node WHERE id IN ({ph})", id_list)
    for nid in ids_to_delete:
        ctx.node_index.pop(nid, None)


def _build_mptt_rows(root: Any) -> list[tuple[Any, ...]]:
    """Compute MPTT (lft, rgt, depth) for all nodes via preorder traversal.

    Args:
        root: Root LazyTree node.

    Returns:
        List of ``(id, parent_id, lft, rgt, depth, is_leaf, name, dist, support)``
        tuples, one per node, in preorder.
    """
    counter = [1]
    rows: list[tuple[Any, ...]] = []

    def walk(node: Any, parent_id: int | None, depth: int) -> None:
        lft = counter[0]
        counter[0] += 1
        slot = len(rows)
        rows.append(())
        for child in node.children:
            walk(child, node._store_id, depth + 1)
        rgt = counter[0]
        counter[0] += 1
        is_leaf = 1 if node.is_leaf else 0
        name = node.name if node.name not in (None, "") else None
        dist = node.dist if node.dist is not None else None
        support = node.support if node.support is not None else None
        rows[slot] = (
            node._store_id, parent_id, lft, rgt, depth, is_leaf, name, dist, support
        )

    walk(root, None, 0)
    return rows


def _sync_topology(
    conn: Any,
    root: Any,
    ctx: BackendContext,
) -> None:
    """Recompute MPTT and sync the in-memory tree structure to the DB.

    Args:
        conn: Writable SQLite connection.
        root: Root ``LazyTree`` node.
        ctx: Active ``BackendContext``.
    """
    in_memory, new_nodes = _collect_in_memory(root)
    _assign_new_node_ids(conn, ctx, in_memory, new_nodes)
    _delete_removed_nodes(conn, ctx, in_memory)
    rows = _build_mptt_rows(root)
    with conn:
        conn.executemany(
            "INSERT OR REPLACE INTO node"
            "(id, parent_id, lft, rgt, depth, is_leaf, name, dist, support)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            rows,
        )


__all__ = ["LazyTree"]
