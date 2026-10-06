"""Explicitly activate the configured policy without replacing analysis history."""

from .risk_context import load_risk_context
from .settings import Settings
from .storage import SQLiteStore


def main():
    settings = Settings()
    catalog, _ = load_risk_context(settings.path(settings.risk_context_path))
    store = SQLiteStore(settings.path(settings.database_path))
    current = store.active_risk_context()
    revision = store.save_risk_context(
        catalog, current["revision_id"] if current else None
    )
    print(f"Activated policy {revision['version']} ({revision['hash']}).")


if __name__ == "__main__":
    main()
