"""Default data-classes for delivery elements.

Any **delivery element** has two terminals and moves electricity from
one bus to another. Cables and transformers fit into this category. Any
edge in supra graph corresponds to one and only one delivery element,
and vice versa.

.. note::
    Whether the element is paralleled should be specified as an edge
    attribute.

.. warning::
    Inherited attributes are not shown again.
"""
from dataclasses import dataclass
from typing import List

import numpy as np
import pandapower as pp
from pandapower.auxiliary import pandapowerNet


@dataclass
class CableEssential:
    """Essential cable parameters."""

    length_km: float  #: cable length in kilometer
    name: str  #: name
    parallel: int  #: number of same cables in parallel


@dataclass
class CablePhase(CableEssential):
    """Define cable phase-by-phase from parameters."""

    phases: List[str]  #: phase(s) of the cable
    r_ohm_mat: np.ndarray  #: resistance matrix in ohm per kilo-meter
    x_ohm_mat: np.ndarray  #: reactance matrix in ohm per kilo-meter

    @property
    def z_ohm_mat(self) -> np.ndarray:
        """Calculate impedance matrix based on resistance and reactance.

        Returns:
            Impedance matrix of the cable.
        """
        return self.r_ohm_mat + 1j * self.x_ohm_mat


@dataclass
class Cable(CableEssential):
    """Define cable from parameters."""

    r_ohm: float  #: resistance in ohm per kilo-meter
    x_ohm: float  #: reactance in ohm per kilo-meter
    c_nf: float  #: capacitance in nano Farad per kilo-meter
    max_i_ka: float  #: maximum thermal current in kilo-ampere

    def update_pandapower(
        self, net: pandapowerNet, source: str, target: str,
    ):
        """Update a pandapower model by adding the cable itself.

        Args:
            net: a pandapower network model.
            source: a bus of the cable, corresponding to ``source`` in
                ``networkx`` edge.
            target: another bus of the cable, corresponding to ``source`` in
                ``networkx`` edge.
        """
        from_bus = pp.get_element_index(net, "bus", source)
        to_bus = pp.get_element_index(net, "bus", target)
        pp.create_line_from_parameters(
            net,
            name=self.name,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=self.length_km,
            r_ohm_per_km=self.r_ohm,
            x_ohm_per_km=self.x_ohm,
            c_nf_per_km=self.c_nf,
            max_i_ka=self.max_i_ka,
            parallel=self.parallel,
        )


@dataclass
class CableStd(CableEssential):
    """Define cable from standard type."""

    std_type: str  #: a standard cable type


@dataclass
class TransformerStd:
    """Essential transformer parameters."""

    std_type: str  #: a standard transformer type
    name: str  #: name of the inter-node
    parallel: int  #: number of same transformers in parallel.

    def update_pandapower(
        self, net: pandapowerNet, source: str, target: str,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            source: a bus of the transformer, corresponding to ``source`` in
                ``networkx`` edge.
            target: another bus of the transformer, corresponding to
                ``source`` in ``networkx`` edge.
        """
        hv_bus = pp.get_element_index(net, "bus", source)
        lv_bus = pp.get_element_index(net, "bus", target)
        pp.create_transformer(
            net,
            name=self.name,
            hv_bus=hv_bus,
            lv_bus=lv_bus,
            std_type=self.std_type,
            parallel=self.parallel,
        )


@dataclass
class Transformer:
    """Define transformer from parameters."""

    pass
