"""Define data-classes for element types."""
from dataclasses import dataclass


@dataclass
class TransformerType:
    """One-phase equivalent transformer type."""

    sn_mva: float  #: rated apparent power in mega-voltampere
    voltage_high_kv: str  #: nominal high voltage in kilo-volt
    voltage_low_kv: str  #: nominal low voltage in kilo-volt
    #: real part of relative short-circuit voltage in percent
    vk_percent: float
    vkr_percent: float  #: relative short-circuit voltage in percent
    pfe_kw: float  #: iron losses in kilo-watt
    i0_percent: float  #: open loop losses in percent
