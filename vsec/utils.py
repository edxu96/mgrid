"""Utility functions to handle associated dataframes."""
from typing import Tuple

from loguru import logger


def join_terminal_labels(edge: Tuple[str, str]) -> str:
    """Join labels of two terminals of a contracted edge.

    Args:
        edge: an edge to be contracted.

    Returns:
        Label of the new node.
    """
    if not (isinstance(edge[0], str) and isinstance(edge[0], str)):
        res = str(edge[0]) + str(edge[1])
        logger.warning("Some label is not string, which might be problematic.")
    else:
        res = edge[0] + edge[1]
    return res


# TODO: (#26) function to rename dataframes associated with edges.
