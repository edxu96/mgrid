"""Define data-classes for element types."""
from dataclasses import dataclass

import pandapower as pp
from pandapower.auxiliary import pandapowerNet


@dataclass
class TransformerType:
    """One-phase equivalent transformer type."""

    s_mva: float  #: nominal apparent power in mega-voltampere
    v_high_kv: float  #: nominal high voltage in kilo-volt
    v_low_kv: float  #: nominal low voltage in kilo-volt
    #: real part of relative short-circuit voltage in percent
    vk_percent: float
    vkr_percent: float  #: relative short-circuit voltage in percent
    pfe_kw: float  #: iron losses in kilo-watt
    i0_percent: float  #: open loop losses in percent

    def update_pandapower(self, net: pandapowerNet, name: str):
        """Update a pandapower model by adding this transformer type.

        Args:
            net: a pandapower network model.
            name: name of this transformer type.
        """
        data = {
            "sn_mva": self.s_mva,
            "vn_hv_kv": self.v_high_kv,
            "vn_lv_kv": self.v_low_kv,
            "vk_percent": self.vk_percent,
            "vkr_percent": self.vkr_percent,
            "pfe_kw": self.pfe_kw,
            "i0_percent": self.i0_percent,
            "shift_degree": 0,
        }
        pp.create_std_type(net, data, name=name, element="trafo")
