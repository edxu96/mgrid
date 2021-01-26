"""Multilayer network for power grid with multiple voltage levels.

The multilayer network in this package has the following features:

- Inter-edges only exist between consecutive layers.
- Nodes are never replicated or related, except those associated with
  inter-edges. So the network is not multiplex network, multi-slice,
  network, or network of networks for sure.

"""
from mgrid.convert import planar2supra
from mgrid.multilayer import SupraGrid
from mgrid.planar import PlanarGrid

__version__ = "0.2.0"
__all__ = [
    "planar2supra",
    "SupraGrid",
    "PlanarGrid",
]
