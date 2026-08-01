"""
Backward-compatibility shim
============================

This module re-exports the entire public API of the ``collapse``
package so that existing notebooks (``import disentanglement as dis``,
``from disentanglement import *``) continue to work without changes.

**New code should import from the** ``collapse`` **package directly.**
"""

# Re-export everything from the collapse package
from collapse import *  # noqa: F401, F403
