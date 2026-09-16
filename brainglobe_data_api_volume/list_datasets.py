"""
Functionality to list all available and downloaded
datasets served by the BrainGlobe data API.
"""

import re
from typing import Any, Dict, List, Optional

import s3fs
from brainglobe_atlasapi import config
from brainglobe_atlasapi.utils import check_s3_status, get_latest_version
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

from brainglobe_data_api_volume.descriptors import (
    DATA_ROOTDIR,
    MANIFESTS_ROOTDIR,
    remote_url_data_s3,
)

# Version folders are written as e.g. "3_0" by the packaging wrapup:
VERSION_PATTERN = re.compile(r"^\d+(?:_\d+)*$")


def folder_version_to_dotted(version: Optional[str]) -> Optional[str]:
    """Convert on-disk version folder names (e.g. 3_0) to dotted form (3.0)."""
    if version is None:
        return None
    return version.replace("_", ".")


def get_manifests_dir(brainglobe_dir=None):
    """Return the local directory holding the dataset manifests.

    Parameters
    ----------
    brainglobe_dir : str or Path object, optional
        Parent of the data API directory. Defaults to the directory in the
        BrainGlobe configuration file.

    Returns
    -------
    Path object
        The ``brainglobe-data-api/manifests`` directory.
    """
    if brainglobe_dir is None:
        brainglobe_dir = config.get_brainglobe_dir()

    return brainglobe_dir / DATA_ROOTDIR / MANIFESTS_ROOTDIR


def _local_versions(dataset_dir) -> List[str]:
    """List the version folders of a dataset that hold a manifest."""
    if not dataset_dir.is_dir():
        return []

    return [
        p.name
        for p in dataset_dir.iterdir()
        if VERSION_PATTERN.match(p.name) and (p / "manifest.json").is_file()
    ]


def get_downloaded_datasets(brainglobe_dir=None) -> List[str]:
    """Get a list of all the downloaded datasets.

    A dataset counts as downloaded once at least one version of its manifest
    is present; the volumes it lists are fetched lazily on first access.

    Returns
    -------
    List[str]
        A sorted list of the locally available datasets.
    """
    manifests_dir = get_manifests_dir(brainglobe_dir)

    if not manifests_dir.exists():
        return []

    return sorted(
        f.name for f in manifests_dir.iterdir() if _local_versions(f)
    )


def get_local_dataset_version(
    dataset_name: str, brainglobe_dir=None
) -> Optional[str]:
    """Get version of a downloaded dataset.

    Arguments
    ---------
    dataset_name : str
        Name of the dataset.

    Returns
    -------
    Optional[str]
        Dotted version of the dataset, or None if it is not downloaded.
    """
    available_versions = _local_versions(
        get_manifests_dir(brainglobe_dir) / dataset_name
    )

    if not available_versions:
        print(f"No dataset found with the name: {dataset_name}")
        return None

    return folder_version_to_dotted(get_latest_version(available_versions))


def get_all_datasets_lastversions() -> Dict[str, str]:
    """Read the last version of every dataset served by the data API.

    The datasets are listed directly from the S3 bucket, one prefix per
    dataset under the manifests root.

    Returns
    -------
    Dict[str, str]
        Mapping of dataset name to its latest dotted version. Empty if the
        bucket cannot be reached.
    """
    if not check_s3_status(raise_error=False):
        print("Cannot fetch the latest dataset versions from the server.")
        return {}

    fs = s3fs.S3FileSystem(anon=True)
    manifests_path = remote_url_data_s3.format(MANIFESTS_ROOTDIR)

    if not fs.exists(manifests_path):
        return {}

    datasets = {}
    for dataset_path in fs.ls(manifests_path):
        dataset_name = dataset_path.rstrip("/").split("/")[-1]
        if dataset_name == MANIFESTS_ROOTDIR:
            # s3fs lists the prefix itself alongside its children
            continue

        versions = [
            version_path.rstrip("/").split("/")[-1]
            for version_path in fs.ls(dataset_path)
        ]
        versions = [v for v in versions if VERSION_PATTERN.match(v)]

        if versions:
            datasets[dataset_name] = folder_version_to_dotted(
                get_latest_version(versions)
            )

    return datasets


def get_datasets_lastversions(
    brainglobe_dir=None,
) -> Dict[str, Dict[str, Any]]:
    """
    Return a dictionary of dataset metadata for the downloaded datasets.

    Returns
    -------
    dict
        A dictionary with metadata about already downloaded datasets. The
        ``version`` and ``latest_version`` fields use the same dotted form
        (e.g. ``3.0``). ``latest_version`` is empty, and ``updated`` None,
        for datasets that the server does not list (custom or offline).
    """
    available_datasets = get_all_datasets_lastversions()

    manifests_dir = get_manifests_dir(brainglobe_dir)

    datasets = {}
    for name in get_downloaded_datasets(brainglobe_dir):
        local_version = get_local_dataset_version(name, brainglobe_dir)
        latest = available_datasets.get(name, "")
        datasets[name] = dict(
            downloaded=True,
            local=str(manifests_dir / name),
            version=local_version,
            latest_version=latest,
            updated=local_version == latest if latest else None,
        )
    return datasets


def show_datasets(
    show_local_path: bool = False, table_width: int = 88
) -> None:
    """
    Print a formatted table with the name and version of local (downloaded)
    and online (available) datasets.

    Parameters
    ----------
    show_local_path : bool, optional
        If True, includes the local path of the datasets
        in the table (default is False).
    table_width : int, optional
        The width of the table to be printed (default is 88).

    Returns
    -------
    None

    """
    available_datasets = get_all_datasets_lastversions()

    # Get local datasets
    downloaded_datasets = get_datasets_lastversions()

    # Get datasets not yet downloaded
    non_downloaded_datasets = {}
    for dataset in available_datasets.keys():
        if dataset not in downloaded_datasets.keys():
            non_downloaded_datasets[str(dataset)] = dict(
                downloaded=False,
                local="",
                version="",
                latest_version=str(available_datasets[dataset]),
                updated=None,
            )

    # Create table
    table = Table(
        show_header=True,
        header_style="bold green",
        show_lines=True,
        expand=False,
        box=None,
    )

    table.add_column("Name", no_wrap=True, width=32)
    table.add_column("Downloaded", justify="center")
    table.add_column("Updated", justify="center")
    table.add_column("Local version", justify="center")
    table.add_column("Latest version", justify="center")
    if show_local_path:
        table.add_column("Local path")

    # Add downloaded datasets (sorted) to the table first
    for dataset_name in sorted(downloaded_datasets.keys()):
        dataset = downloaded_datasets[dataset_name]
        table = add_dataset_to_row(
            dataset_name, dataset, table, show_local_path=show_local_path
        )

    # Then add non-downloaded datasets (sorted) to the table
    for dataset_name in sorted(non_downloaded_datasets.keys()):
        dataset = non_downloaded_datasets[dataset_name]
        table = add_dataset_to_row(
            dataset_name, dataset, table, show_local_path=show_local_path
        )

    # Print the resulting table
    rprint(
        Panel.fit(
            table,
            width=table_width,
            title="BrainGlobe Datasets",
        )
    )


def add_dataset_to_row(
    dataset: str,
    info: Dict[str, Any],
    table: Table,
    show_local_path: bool = False,
) -> Table:
    """
    Add information about each dataset to a row of the rich table.

    Parameters
    ----------
    dataset : str
        The name of the dataset.
    info : dict
        A dictionary containing information about the dataset.
    table : rich.table.Table
        The table to which the row will be added.
    show_local_path : bool, optional
        If True, includes the local path of the dataset
        in the row (default is False).

    Returns
    -------
    rich.table.Table
        The updated table with the new row added.

    """
    if info["downloaded"]:
        downloaded = "[green]:heavy_check_mark:[/green]"

        if info["updated"] is None:
            updated = ""
        elif info["updated"]:
            updated = "[green]:heavy_check_mark:[/green]"
        else:
            updated = "[red dim]x"

    else:
        downloaded = ""
        updated = ""

    row = [
        "[bold]" + dataset,
        downloaded,
        updated,
        (
            "[#c4c4c4]" + info["version"]
            if info["version"] and "-" not in info["version"]
            else ""
        ),
        "[#c4c4c4]" + info["latest_version"],
    ]

    if show_local_path:
        row.append(info["local"])

    table.add_row(*row)

    return table
