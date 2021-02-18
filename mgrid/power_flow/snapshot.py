"""Store input and calculation results in snapshots.

Though the power system operates continuously, it is considered in
discrete time in power flow calculation. That is, between two
consecutive time indices, the system state is assumed to remain steady,
so small variations are ignored. Usually, the duration between indices
is long compared to the frequency of alternating current (50 Hz in
Europe and 60 Hz in the US).
"""
