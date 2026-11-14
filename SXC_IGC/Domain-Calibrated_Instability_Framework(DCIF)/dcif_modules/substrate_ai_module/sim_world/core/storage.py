from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .errors import RevisionNotFoundError, StorageError
from .ids import RevisionId
from .revision import Revision


@dataclass
class InMemoryStorage:
    _revisions: dict[RevisionId, Revision] = field(default_factory=dict)
    _history: list[RevisionId] = field(default_factory=list)
    _latest: RevisionId | None = None

    def save_revision(self, revision: Revision) -> Revision:
        if revision.revision_id in self._revisions and revision.revision_id != self._latest:
            raise StorageError(f"revision already exists: {revision.revision_id}")
        self._revisions[revision.revision_id] = revision
        if not self._history or self._history[-1] != revision.revision_id:
            self._history.append(revision.revision_id)
        self._latest = revision.revision_id
        return revision

    def load_revision(self, revision_id: RevisionId) -> Revision:
        try:
            return self._revisions[revision_id]
        except KeyError as exc:
            raise RevisionNotFoundError(f"revision not found: {revision_id}") from exc

    def latest_revision(self) -> Revision | None:
        if self._latest is None:
            return None
        return self._revisions[self._latest]

    def rollback(self, revision_id: RevisionId) -> Revision:
        revision = self.load_revision(revision_id)
        self._latest = revision.revision_id
        return revision

    def list_history(self) -> tuple[Revision, ...]:
        return tuple(self._revisions[revision_id] for revision_id in self._history)
