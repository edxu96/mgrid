"""Define classes for elements using ``pandapower``.

.. note:
    Whether the element is paralleled should be specified as an edge
    attribute.

"""
from dataclasses import dataclass


@dataclass
class _CableEssential:
    """Essential cable parameters."""

    length_km: float


@dataclass
class Cable(_CableEssential):
    """Define cable from parameters."""

    r_ohm_per_km: float
    x_ohm_per_km: float
    c_nf_per_km: float
    max_i_ka: float


@dataclass
class CableStd(_CableEssential):
    """Define cable from standard type."""

    std_type: str


@dataclass
class TransformerStd:
    """Essential transformer parameters."""

    std_type: str


@dataclass
class Transformer:
    """Define transformer from parameters."""

    pass


@dataclass
class Ejection:
    """Essential parameters for load or static generators."""

    p_mw: float
    q_mvar: float


@dataclass
class ExternalGrid:
    """Define a slack bus and a corresponding external grid."""

    vm_pu: float
