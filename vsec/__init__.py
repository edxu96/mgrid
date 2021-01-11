"""Main module for ``vsec``."""
from vsec.conversion import contract, split
from vsec.geometry import GeoGraph
from vsec.graph import WeightGraph

__version__ = "0.1.0"
__all__ = [
    "contract",
    "split",
    "GeoGraph",
    "WeightGraph",
]
