"""
Compatibility package.

The codebase lives under `agentic_search/`, but some consumers (including this
repo's tests) import modules from a top-level `core` package.

Keep this shim thin: re-export from `agentic_search.core.*`.
"""

from importlib import import_module as _import_module
from typing import Any as _Any


def __getattr__(name: str) -> _Any:  # pragma: no cover
    # Allow `import core; core.utils` style access.
    try:
        return _import_module(f"agentic_search.core.{name}")
    except ModuleNotFoundError as e:
        raise AttributeError(name) from e

