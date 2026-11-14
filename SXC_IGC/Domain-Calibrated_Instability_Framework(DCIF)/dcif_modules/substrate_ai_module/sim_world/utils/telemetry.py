import os
import json
from datetime import datetime
from typing import Any, Mapping
from types import MappingProxyType

_ENABLED = bool(os.environ.get("PHASE4_1_TELEMETRY", ""))
_OUT_DIR = os.environ.get("PHASE4_1_OUTPUT_DIR", "phase4_1_output")


def _safe_serialize(obj: Any, _visited: set[int] | None = None, _depth: int = 0) -> Any:
    """Recursively convert common non-JSON-native objects into JSON-safe forms.

    This is for telemetry only — it must not mutate runtime objects.
    It handles MappingProxyType, mappings, sequences, numpy arrays, dataclass-like
    objects, and falls back to string representations for unknowns. It also
    avoids infinite recursion via an identity-based visited set and depth limit.
    """
    if _visited is None:
        _visited = set()
    try:
        import numpy as _np
    except Exception:
        _np = None

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if _depth > 10:
        try:
            return repr(obj)
        except Exception:
            return str(obj)
    obj_id = id(obj)
    if obj_id in _visited:
        return repr(obj)
    _visited.add(obj_id)

    # Bytes -> decode
    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except Exception:
            return str(obj)

    # MappingProxy -> dict
    if isinstance(obj, MappingProxyType):
        try:
            return _safe_serialize(dict(obj), _visited, _depth + 1)
        except Exception:
            return dict((str(k), _safe_serialize(v, _visited, _depth + 1)) for k, v in obj.items())

    # Mappings
    if isinstance(obj, Mapping):
        result = {}
        for k, v in obj.items():
            try:
                key = str(k)
            except Exception:
                key = repr(k)
            result[key] = _safe_serialize(v, _visited, _depth + 1)
        return result

    # Numpy arrays and scalars
    if _np is not None:
        try:
            if isinstance(obj, _np.ndarray):
                return obj.tolist()
            if isinstance(obj, (_np.generic,)):
                return obj.item()
        except Exception:
            pass

    # Sequences
    if isinstance(obj, (list, tuple, set)):
        return [_safe_serialize(v, _visited, _depth + 1) for v in obj]

    # Objects with __dict__ (dataclasses, simple objects)
    if hasattr(obj, "__dict__"):
        try:
            return _safe_serialize(vars(obj), _visited, _depth + 1)
        except Exception:
            pass

    # Fallback to string representation
    try:
        return str(obj)
    except Exception:
        return repr(obj)


def emit(event: Mapping[str, Any]) -> None:
    if not _ENABLED:
        return
    try:
        os.makedirs(_OUT_DIR, exist_ok=True)
        path = os.path.join(_OUT_DIR, "telemetry.jsonl")
        record = _safe_serialize(dict(event))
        record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Telemetry must not raise
        return
