"""
This module contains all the elements necessary to:

- Launch a backend server to receive drawing (and other) requests and
  send back the graphic commands and other information (``explorer``)
- Define how to visualize trees (``layout``)
- Use pieces of drawn information attached to the nodes (``faces``)

The drawing logic exists in the ``draw`` submodule, the basic graphical
elements that can be sent are defined in the ``graphics`` submodule,
and the basic coordinate functions are defined in ``coordinates``.
"""

from .layout import Layout, BASIC_LAYOUT
from .faces import (EvalTextFace, TextFace, TextArrayFace, PropFace,
                    CircleFace, PolygonFace, BoxFace, RectFace,
                    ImageFace, SeqFace, HeatmapFace, LegendFace)
