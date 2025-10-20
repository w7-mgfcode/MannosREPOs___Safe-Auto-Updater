"""
REST API module for Safe Auto-Updater.
"""

from .server import create_app, start_server

__all__ = ['create_app', 'start_server']
