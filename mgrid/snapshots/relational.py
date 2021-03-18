"""Store snapshots in SQLite database."""
import pathlib
import sqlite3
from typing import List, Optional, Union

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
    """Database for snapshots of a directed graph."""

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

    def add(self, source: str, target: str, element: Optional[int] = 0):
        """Add a new edge.

        Args:
            source: one terminal of the edge.
            target: the other terminal of the edge.
            element: index of the element representing the edge.
        """
        with self.conn:
            query = """
                INSERT INTO edges (source, target, element)
                VALUES(:source, :target, :element);
            """
            self.conn.execute(
                query, {"source": source, "target": target, "element": element}
            )

    def branch(self, name: str, links: Union[str, List[str]]):
        """Init a new snapshot and specify its links.

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

    def take(self):
        """Take the snapshot."""
        pass
