"""Install a versioned demo database once, without modifying existing runtime data."""

import os
import shutil
import tempfile
from pathlib import Path


def bootstrap_database(destination: Path, snapshot: Path):
    if destination.resolve() == snapshot.resolve():
        raise RuntimeError(
            "DATABASE_PATH must differ from the read-only demo snapshot."
        )
    if destination.exists():
        return
    if not snapshot.is_file():
        raise RuntimeError(
            "Configure a readable BOOTSTRAP_DATABASE_PATH or disable it."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as file:
            temporary = Path(file.name)
            with snapshot.open("rb") as source:
                shutil.copyfileobj(source, file)
            file.flush()
            os.fsync(file.fileno())
        # Publish only a complete copy; never replace a database created concurrently.
        try:
            os.link(temporary, destination)
        except FileExistsError:
            pass
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
