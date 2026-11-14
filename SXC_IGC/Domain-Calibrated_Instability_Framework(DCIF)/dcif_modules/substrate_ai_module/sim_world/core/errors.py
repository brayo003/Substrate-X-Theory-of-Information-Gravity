class SimWorldError(Exception):
    """Base error for the SimWorld runtime."""


class ValidationError(SimWorldError):
    """Raised when an action or transition fails validation."""


class ConflictError(SimWorldError):
    """Raised when a transition conflicts with authoritative state."""


class RevisionNotFoundError(SimWorldError):
    """Raised when a requested revision does not exist."""


class SnapshotError(SimWorldError):
    """Raised when a snapshot cannot be created or restored."""


class StorageError(SimWorldError):
    """Raised when the in-memory storage backend cannot satisfy a request."""


class RollbackError(SimWorldError):
    """Raised when rollback is disallowed or cannot be completed."""


class VerificationError(SimWorldError):
    """Raised when verification cannot be completed."""
