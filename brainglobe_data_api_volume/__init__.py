from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brainglobe-data-api-volume")
except PackageNotFoundError:
    # package is not installed
    pass
