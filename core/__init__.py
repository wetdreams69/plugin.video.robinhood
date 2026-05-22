"""Core utilities package initializer.
Ensures `from core.http_client import HttpClient` works in all environments
including Kodi's bundled Python which may not support implicit namespace packages.
"""
__all__ = ["http_client"]
