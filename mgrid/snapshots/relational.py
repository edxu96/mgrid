"""Store snapshots for a graph in an SQLite database."""
import pathlib
import sqlite3
from typing import Generator, List, Optional, Set, Tuple, Union

# import networkx as nx

from mgrid.log import LOGGER

INIT_TABLES = """
    CREATE TABLE edges (
        source TEXT,
        target TEXT,
        element INTEGER,
        PRIMARY KEY (source, target)
    );
    CREATE UNIQUE INDEX edges_inv ON edges (target, source);

    CREATE TABLE snapshots (name TEXT PRIMARY KEY);

    CREATE TABLE events (
        snapshot TEXT NOT NULL,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        FOREIGN KEY (snapshot) REFERENCES snapshots (name),
        FOREIGN KEY (source, target) REFERENCES edges (source, target)
    );

    CREATE TABLE links (
        snapshot TEXT NOT NULL,
        link TEXT NOT NULL,
        FOREIGN KEY (snapshot) REFERENCES snapshots (name),
        FOREIGN KEY (link) REFERENCES snapshots (name)
    );
"""


class GraphSnapshots:
    """Database for snapshots of a directed graph.

    Attributes:
        cursor (Union[sqlite3.Cursor, None]): a temporary cursor.
    """

    def __init__(self, path: str):
        """Initialise an object for a database for snapshots.

        If the path is not directed to a database file.

        Args:
            path: to the database file.
        """
        if path == ":memory:":
            self.conn = self._init_conn(path)
            self._init_tables()
        elif pathlib.Path(path).is_file() and path.endswith(".db"):
            self.conn = self._init_conn(path)
        elif not pathlib.Path(path).exists() and path.endswith(".db"):
            self.conn = self._init_conn(path)
            self._init_tables()

        self.cursor = None

    def _init_tables(self):
        """Initialise tables in a database for snapshots."""
        with self.conn:
            self.conn.executescript(INIT_TABLES)
            LOGGER.info(
                "A new database for snapshots of a graph has been initiated."
            )

            self.conn.execute("INSERT INTO snapshots (name) VALUES ('head');")
            LOGGER.debug(
                'A new snapshot "head" without any link has been branched.'
            )

    @staticmethod
    def _init_conn(path: str) -> sqlite3.Connection:
        """Initialise database connection.

        Args:
            path: to an existing or a new database file.

        Returns:
            Connection to the database.
        """
        try:
            return sqlite3.connect(path)
        except sqlite3.Error:
            LOGGER.exception("SQLite DB connection failed.")

    def _select_direct_links(self, snapshot: str) -> Set[str]:
        """Select all the direct links of a given snapshot.

        Args:
            snapshot: the name of an existing snapshot.

        Returns:
            A set of all the directly linked snapshots.
        """
        with self.conn:
            links = self.conn.execute(
                "SELECT * FROM links WHERE snapshot = :snapshot",
                {"snapshot": snapshot},
            ).fetchmany()
            res = {link[1] for link in links}

        if len(res) == 0:
            LOGGER.critical(f'Snapshot "{snapshot}" has no link.')
            res = None
        return res

    def _get_links(self, snapshot: str) -> Set[str]:
        """Get all the links of a given snapshot.

        Args:
            snapshot: the name of an existing snapshot.

        Returns:
            A set of all the linked snapshots.
        """
        checked = {"head"}
        links = self._select_direct_links(snapshot)
        while len(links - checked) > 0:
            poped = (links - checked).pop()
            checked.update(poped)
            links.update(self._select_direct_links(poped))

        LOGGER.debug(f'Snapshot "{snapshot}" is linked to "{links}".')
        return links

    # def read(self, snapshot: str) -> nx.DiGraph:
    #     """Get the corresponding directed graph of a snapshot.

    #     Args:
    #         snapshot: the name of an existing snapshot.

    #     Returns:
    #         A ``networkx`` directed graph.
    #     """
    #     links = self._get_links(snapshot)
    #     print(links)

    def add_edges(self, edges: Generator[Tuple[str, str, int], None, None]):
        """Add multiple edges to the current snapshot in progress.

        Args:
            edges: a generator for tuples with three values indicating
                source, target and element index.
        """
        if self.cursor is None:
            LOGGER.error("A new pose must be created first.")
        else:
            query = """
                INSERT INTO edges (source, target, element)
                VALUES(?, ?, ?);
            """
            self.cursor.executemany(query, edges)

    def add_edge(self, source: str, target: str, element: Optional[int] = 0):
        """Add a new edge to the current snapshot in progress.

        Args:
            source: one terminal of the edge.
            target: the other terminal of the edge.
            element: index of the element representing the edge.
        """
        if self.cursor is None:
            LOGGER.error("A new pose must be created first.")
        else:
            query = """
                INSERT INTO edges (source, target, element)
                VALUES(:source, :target, :element);
            """
            self.cursor.execute(
                query, {"source": source, "target": target, "element": element}
            )

    # @property
    # def current_graph(self) -> nx.DiGraph:
    #     """Get the graph based on the current snapshot in progress.

    #     Returns:
    #         A ``networkx`` directed graph based on the working branch.
    #     """
    #     if self.cursor is None:
    #         LOGGER.error('A new pose must be created first.')
    #     else:
    #         pass

    def pose(self, name: str, links: Union[str, List[str]]):
        """Specify links for a new snapshot.

        Note:
            - This function is the first step for a new snapshot. It is
              similar to the beginning of a transaction, but it can be
              based on different increment(s).
            - Links can be modified later before committing.

        Args:
            name: name of the snapshot.
            links: other snapshots to which it is linked.
        """
        with self.conn:
            self.conn.execute(
                "INSERT INTO snapshots (name) VALUES (:name);", {"name": name}
            )

            # Insert snapshot links one-by-one.
            insertion = """
                INSERT INTO links (snapshot, link) VALUES (:snapshot, :link)
            """
            if isinstance(links, str):
                links = [links]
            for link in links:
                self.conn.execute(insertion, {"snapshot": name, "link": link})
            LOGGER.info(
                f'A new snapshot "{name}" linked to {links} has been branched.'
            )

        self.cursor = self.conn.cursor()

    def rollback(self):
        """Drop the new snapshot and delete all the modifications."""
        pass

    def commit(self):
        """Take the new snapshot and forbid further modification."""
        pass
