"""Default data-classes for conversion elements."""
from dataclasses import dataclass

from pandapower.auxiliary import pandapowerNet


@dataclass
class Ejection:
    """Essential parameters for load or static generators."""

    p_mw: float  #: ejected real power in mega-watt
    power_factor: float  #: power factory

    @property
    def q_mw(self) -> float:
        """Calculate ejected reactive power in mega-watt.

        Returns:
            Ejected reactive power in mega-watt.
        """
        return ((self.p_mw / self.power_factor) ** 2 - self.p_mw ** 2) ** 0.5


@dataclass
class ExternalGrid:
    """Define a slack bus and a corresponding external grid.

    Note:
        It's assumed that there is only one slack bus and one external
        grid.
    """

    vm_pu: float  #: voltage magnitude in per unit

    def update_pandapower(
        self, net: pandapowerNet, name: str, bus: str,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            name: name of the external grid.
            bus: the bus to which the external grid is attached.
        """
        net.add("Generator", name=name, bus=bus, control="Slack")
