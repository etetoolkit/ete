"""ete4.lazytree — LazyTree and its backing infrastructure.

Public surface:
    LazyTree        — ete4.Tree backed by an etestore .ete file
    BackendContext  — per-session store state shared across all nodes
    LazyPropsDict   — dict subclass that fetches missing props from the store
"""

from ete4.lazytree.tree import LazyTree
from ete4.lazytree.backend import BackendContext, LazyPropsDict, _force_set_props

__all__ = ["LazyTree", "BackendContext", "LazyPropsDict", "_force_set_props"]
