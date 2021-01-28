"""Test class ``SupraGrid``."""
from collections import namedtuple

import pandas as pd
from tabulate import tabulate

Column = namedtuple(
    "Column",
    ["name", "dtype", "definition", "is_index"],
    defaults=[None, None, None, False],
)
Index = namedtuple(
    "Index",
    ["name", "dtype", "definition", "is_index"],
    defaults=[None, None, None, True],
)


INTRA = pd.DataFrame(
    [
        Index("source_original", "object", "source in planar graph"),
        Index("target_original", "object", "target in planar graph"),
        Column("source", "object", "current source node"),
        Column("target", "object", "current target node"),
    ]
)
INTER = pd.DataFrame(
    [
        Column("upper", "int64", "integer index of upper layer"),
        Column("lower", "int64", "integer index of lower layer"),
        Column("source", "object", "source node in supra graph"),
        Column("target", "object", "target node in supra graph"),
    ]
)
NODE = pd.DataFrame(
    [
        Index("name", "object", "node name"),
        Column("layer", "int64", "integer index of layer"),
    ]
)


def test_print_columns():
    """Print columns of dataframes."""
    print(tabulate(INTRA, headers="keys", tablefmt="rst", showindex=False))
    print(tabulate(INTER, headers="keys", tablefmt="rst", showindex=False))
    print(tabulate(NODE, headers="keys", tablefmt="rst", showindex=False))
