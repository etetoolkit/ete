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


from ete4.lazytree.backend import (
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

    __slots__ = ("_store", "_store_id", "_draw_debug")

    # ------------------------------------------------------------------
    # constructor
    # ------------------------------------------------------------------

    def __init__(self, data: Any = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        # Will be assigned by LazyTree.open(); None until then.
        self._store: Any = None
        self._store_id: int = -1
        self._draw_debug: dict = {}

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

        ctx = _get_ctx(self)
        if ctx is not None:
            if ctx.mode == "rw":
                ctx.flush_all()
            # Load all lazy props into the dict so from_ete4 can serialise them.
            # save() is a one-shot operation; full memory load is acceptable here.
            _preload_nodes(ctx, list(ctx.node_index.keys()), list(ctx.lazy_props))
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
        zoom: tuple[float, float, float] | None = None,
        node_height_min: float = 0.0,
    ) -> None:
        """Bulk-load lazy props for visible nodes before a SmartView frame.

        Uses ``node.size[1]`` (leaf count) and the viewport y-range to
        traverse only the subtrees whose y-span overlaps the current viewport,
        then issues one ``get_many()`` call for those nodes.  Nodes already in
        the dict cache are skipped; the ``_missing`` set prevents re-querying
        absent props.

        The ``zoom`` / ``node_height_min`` pair mirrors the SmartView collapse
        rule: a node is collapsed (and its children skipped) when
        ``node.size[1] * zy < node_height_min``.  Passing these avoids
        preloading the interiors of collapsed subtrees, which can reduce the
        preload set from thousands of nodes to tens.

        Args:
            viewport: Spatial viewport from SmartView (``[x, y, w, h]`` in
                tree coordinate units where y is in leaf-count space) or
                ``None`` for unrestricted view.
            needed_props: Prop names declared by layouts via ``preload_props``.
                When ``None``, this is a no-op.
            zoom: SmartView zoom tuple ``(zx, zy, za)``.  Only ``zy`` is used.
            node_height_min: Minimum node height in pixels below which a node
                is collapsed.  ``0`` disables the collapse-aware pruning.
        """
        import time as _time
        self._draw_debug: dict = {}
        ctx = _get_ctx(self)
        if ctx is None or not needed_props:
            return
        props = [p for p in needed_props if p in ctx.lazy_props]
        if not props:
            return
        t0 = _time.perf_counter()
        zy = zoom[1] if zoom else 0.0
        visible_nids = _collect_visible_nids(self, viewport, zy, node_height_min)
        if not visible_nids:
            return

        # Skip nodes that already have all needed props cached or confirmed absent.
        # After the first preload frame, _missing is populated for nodes without
        # data, so subsequent frames skip re-querying them immediately.
        props_set = frozenset(props)
        to_fetch: list[int] = []
        for nid in visible_nids:
            node = ctx.node_index.get(nid)
            if node is None:
                continue
            lpd = node.props
            if not isinstance(lpd, LazyPropsDict):
                continue
            for p in props_set:
                if not dict.__contains__(lpd, p) and p not in lpd._missing:
                    to_fetch.append(nid)
                    break
        if to_fetch:
            _preload_nodes(ctx, to_fetch, props)
        self._draw_debug = {
            'n_visible': len(visible_nids),
            'n_cached': len(visible_nids) - len(to_fetch),
            'n_fetched': len(to_fetch),
            't_preload_ms': round((_time.perf_counter() - t0) * 1000, 1),
        }

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
        """Build a LazyTree from an open TreeStore in a single pass.

        Processes raw SQL rows directly — no intermediate TopologyNode or
        TreeTopology objects.  Creates each node, sets its attributes, wires
        the parent-child link, and installs its LazyPropsDict all in one loop,
        reducing allocation pressure and eliminating two full iterations over N.

        Args:
            store: Open ``TreeStore``.
            mode: ``'ro'`` or ``'rw'``.
            eager_props_override: Explicit eager prop list or ``None``.
            lazy_props_override: Explicit lazy prop list or ``None``.

        Returns:
            Root ``LazyTree`` node.
        """
        import gc

        prop_infos = store.list_properties()
        eager_set, lazy_set = _partition_props(
            prop_infos, eager_props_override, lazy_props_override
        )

        # Create the context with an empty node_index before the build loop;
        # LazyPropsDict references ctx, and node_index is filled in-place.
        node_index: dict[int, LazyTree] = {}
        ctx = BackendContext(
            store=store,
            lazy_props=lazy_set,
            eager_props=eager_set,
            mode=mode,
            node_index=node_index,
        )
        store._ctx = ctx

        rows = store.topology_rows()
        if not rows:
            raise RuntimeError("topology is empty")

        # nodes is a local dict for parent lookups; node_index is the ctx copy.
        nodes: dict[int, Any] = {}
        root: LazyTree | None = None

        was_enabled = gc.isenabled()
        gc.disable()
        try:
            for r in rows:
                nid = int(r[0])
                pid = r[1]
                node: LazyTree = cls()
                if r[4] is not None:   # name
                    node.name = r[4]
                if r[3] is not None:   # dist
                    node.dist = r[3]
                node._store = store
                node._store_id = nid
                lpd = LazyPropsDict(nid, ctx, node.props)
                _force_set_props(node, lpd)
                nodes[nid] = node
                node_index[nid] = node
                if pid is None:
                    root = node
                else:
                    nodes[int(pid)].add_child(node)
        finally:
            if was_enabled:
                gc.enable()

        if root is None:
            raise RuntimeError("topology has no root")

        _prefetch_eager_props(store, node_index, eager_set)
        return root


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


_MAX_PRELOAD_PER_FRAME: int = 5_000


def _collect_visible_nids(
    root: Any,
    viewport: Any,
    zy: float = 0.0,
    node_height_min: float = 0.0,
) -> list[int]:
    """Return store IDs of nodes whose y-span overlaps the viewport.

    Traverses the tree using ``node.size[1]`` (leaf count in subtree) as the
    y-extent of each node.  Prunes entire subtrees that fall outside the
    viewport, making this O(V log N) where V is the number of visible leaves.

    When ``zy`` and ``node_height_min`` are provided the traversal also stops
    descending into subtrees that would be collapsed by the SmartView renderer
    (``node.size[1] * zy < node_height_min``).  This mirrors the exact collapse
    rule used in :class:`~ete4.smartview.draw.Drawer` and avoids preloading
    the interiors of collapsed subtrees.

    Args:
        root: Root ``LazyTree`` node.
        viewport: ``[x, y, dx, dy]`` box in tree coordinates where y is in
            leaf-count units, or ``None`` for unrestricted view.
        zy: Vertical zoom factor (pixels per leaf unit).  ``0`` disables
            collapse-aware pruning.
        node_height_min: Minimum node height in pixels.  A node whose
            ``size[1] * zy < node_height_min`` is treated as collapsed and its
            children are not visited.  ``0`` disables this pruning.

    Returns:
        List of store IDs (at most ``_MAX_PRELOAD_PER_FRAME``).
    """
    result: list[int] = []
    collapse_threshold: float = (node_height_min / zy) if zy > 0 and node_height_min > 0 else 0.0

    if viewport is None:
        for node in root.traverse():
            if len(result) >= _MAX_PRELOAD_PER_FRAME:
                break
            props = node.props
            if isinstance(props, LazyPropsDict):
                result.append(props._node_id)
        return result

    vp_y: float = viewport[1]
    vp_y_end: float = viewport[1] + viewport[3]

    def _visit(node: Any, y: float) -> None:
        if len(result) >= _MAX_PRELOAD_PER_FRAME:
            return
        dy: float = node.size[1]
        if dy == 0:
            dy = 1.0
        if y + dy <= vp_y or y >= vp_y_end:
            return  # outside viewport — prune
        props = node.props
        if isinstance(props, LazyPropsDict):
            result.append(props._node_id)
        # Stop descending into subtrees the renderer will collapse.
        if collapse_threshold > 0 and dy < collapse_threshold:
            return
        child_y = y
        for child in node.children:
            _visit(child, child_y)
            child_y += child.size[1] or 1.0

    _visit(root, 0.0)
    return result


def _preload_nodes(
    ctx: BackendContext,
    node_ids: list[int],
    props: list[str] | None = None,
) -> None:
    """Bulk-load props into LazyPropsDicts for the given node IDs.

    For each queried (node, prop) pair that returns no data, the prop name is
    added to that node's ``_missing`` set.  This prevents ``_preload_for_draw``
    from re-querying the same absent (node, prop) pairs on subsequent frames.

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
        lpd = node.props
        if not isinstance(lpd, LazyPropsDict):
            continue
        for name in prop_names:
            val = prop_vals.get(name)
            if val is not None:
                dict.__setitem__(lpd, name, val)
            else:
                lpd._missing.add(name)


def _prefetch_eager_props(
    store: Any,
    node_index: dict[int, LazyTree],
    eager_set: frozenset[str],
) -> None:
    """Bulk-load explicitly eager props at open time.

    By default ``eager_set`` is empty (all props are lazy) so this is a
    no-op unless the caller passed ``eager_props_override`` to
    :meth:`LazyTree.open`.

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
    # Default: classify by dtype stored in the catalog — no runtime scanning.
    # Scalar/text dtypes are eager (loaded at open time); blob/array dtypes
    # are lazy (fetched per-frame as nodes become visible).
    eager_set = frozenset(i.name for i in prop_infos if i.dtype in EAGER_DTYPES)
    lazy_set = frozenset(i.name for i in prop_infos if i.dtype not in EAGER_DTYPES)
    return eager_set, lazy_set


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
