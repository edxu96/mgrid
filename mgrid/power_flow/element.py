"""Define classes for elements using ``pandapower``.

.. note::
    Whether the element is paralleled should be specified as an edge
    attribute.

.. warning::
    Inherited attributes are not shown again.

"""
from dataclasses import dataclass


@dataclass
class CableEssential:
    """Essential cable parameters."""

    length_km: float
    """cable length in kilometer"""


@dataclass
class Cable(CableEssential):
    """Define cable from parameters."""

    r_ohm_per_km: float
    """resistance in ohm per kilo-meter"""
    x_ohm_per_km: float
    """reactance in ohm per kilo-meter"""
    c_nf_per_km: float
    """capacitance in nano Farad per kilo-meter"""
    max_i_ka: float
    """maximum thermal current in kilo-ampere"""


@dataclass
class CableStd(CableEssential):
    """Define cable from standard type."""

    std_type: str
    """a standard cable type"""


@dataclass
class TransformerStd:
    """Essential transformer parameters."""

    std_type: str
    """a standard transformer type"""


@dataclass
class Transformer:
    """Define transformer from parameters."""

    pass


@dataclass
class Ejection:
    """Essential parameters for load or static generators."""

    p_mw: float
    """ejected real power in mega-watt"""
    q_mvar: float
    """ejected reactive power in mega-watt"""


@dataclass
class ExternalGrid:
    """Define a slack bus and a corresponding external grid."""

    vm_pu: float
    """voltage magnitude in per unit"""
