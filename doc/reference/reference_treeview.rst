.. module:: treeview
.. currentmodule:: ete4.treeview

.. note::

  Since ETE 4, the treeview module is **not** the preferred way to
  create visualizations. This module is a port of the old
  visualization in ETE, and we have maintained it, but recommend
  instead to use the web visualization (:class:`smartview module
  <ete4.smartview>`).

  This module has less functionality and will not be generally
  updated. Also, please note that the way it uses faces and layouts is
  incompatible with the way smartview uses them.


Treeview (qt graphics)
======================

.. contents::


TreeStyle
---------

.. autoclass:: TreeStyle

.. autoclass:: FaceContainer
   :members:


NodeStyle
---------

.. autoclass:: NodeStyle
   :members:


Faces
-----

.. autofunction:: add_face_to_node

.. autoclass:: Face
   :members:

.. autoclass:: TextFace
   :members:

.. autoclass:: AttrFace
   :members:

.. autoclass:: ImgFace
   :members:

.. autoclass:: CircleFace
   :members:

.. autoclass:: RectFace
   :members:

.. autoclass:: StackedBarFace
   :members:

.. autoclass:: SequenceFace
   :members:

.. autoclass:: SeqMotifFace
   :members:

.. autoclass:: BarChartFace
   :members:

.. autoclass:: PieChartFace
   :members:

.. autoclass:: TreeFace
   :members:

.. autoclass:: StaticItemFace
   :members:

.. autoclass:: DynamicItemFace
   :members:
