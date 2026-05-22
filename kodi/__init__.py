"""Kodi helpers package initializer.
Provides a regular package so imports like `from kodi.api import ...` work
in environments (like Kodi) that don't enable implicit namespace packages.
"""
__all__ = ["api"]
