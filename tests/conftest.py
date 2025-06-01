import pytest
from unittest.mock import MagicMock, patch
import warnings

# Global patcher object to manage the patch's lifecycle
_gi_require_patcher = None

def pytest_configure(config):
    """
    Called after command line options have been parsed and before test collection.
    This is a good place for early, session-wide patches.
    """
    global _gi_require_patcher

    # Attempt to filter PyGIWarnings by importing PyGIWarning here
    try:
        from gi import PyGIWarning
        import gi  # noqa: F401 - Check if gi is available
        gi.require_version('Gtk', '3.0')
        gi.require_version('GdkX11', '3.0')
        _gi_require_patcher = patch('gi.require_version', MagicMock())
        _gi_require_patcher.start()
    except ImportError:
        # If gi or PyGIWarning cannot be imported here, we can't filter by this category.
        pass # The patch below for gi.require_version is the primary mechanism to avoid crashes.

def pytest_unconfigure(config):
    """
    Called before test process is exited. Used to clean up session-wide resources.
    """
    global _gi_require_patcher
    if _gi_require_patcher:
        _gi_require_patcher.stop()
        _gi_require_patcher = None
        # print("DEBUG: pytest_unconfigure - Stopped patch for gi.require_version") # Optional: for debugging