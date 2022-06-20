import importlib.metadata

try:
    __version__ = importlib.metadata.version("reloader_cli")
except:
    __version__ = importlib.metadata.version(__package__ or __name__)
