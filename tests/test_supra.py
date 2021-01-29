"""Test class ``SupraGrid``."""
from collections import namedtuple

import pandas as pd
from pandas.core.frame import DataFrame
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
        Index("node", "object", "name in planar graph"),
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


def print_columns(df: DataFrame):
    """Print info on index and columns as a RST table.

    Args:
        df: info on names and data types of index and columns.
    """
    print(tabulate(df, headers="keys", tablefmt="rst", showindex=False))


def test_print_columns():
    """Print columns of dataframes."""
    print_columns(INTER)
    print_columns(INTRA)
    print_columns(NODE)
