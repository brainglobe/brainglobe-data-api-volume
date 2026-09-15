"""Download volume metadata using current and legacy manifest names."""

import json
from types import SimpleNamespace

import pytest

from brainglobe_data_api_volume import BrainGlobeVolume, bg_volume


@pytest.mark.parametrize("legacy_manifest", [False, True])
@pytest.mark.parametrize("fail_download", [False, True])
def test_volume_download(tmp_path, monkeypatch, legacy_manifest, fail_download):
    key = "additional_references" if legacy_manifest else "volumes"
    metadata = {
        f"{key}_only": True,
        key: [{"name": "gene", "location": "/templates/gene/1_0"}],
    }
    requests = []

    def get(remote, local, **kwargs):
        requests.append(remote)
        if local.name == "manifest.json":
            local.write_text(json.dumps(metadata))
        elif fail_download:
            raise FileNotFoundError("Missing volume metadata")

    monkeypatch.setattr(bg_volume, "check_s3_status", lambda: None)
    dataset = BrainGlobeVolume.__new__(BrainGlobeVolume)
    dataset.brainglobe_dir = tmp_path
    dataset.atlas_name = "test_mouse_25um"
    dataset._remote_version = (1, 0)
    dataset._local_full_name = "stale"
    dataset.fs = SimpleNamespace(get=get)

    if fail_download:
        with pytest.raises(FileNotFoundError, match="Missing volume metadata"):
            dataset.download()
        assert not list(tmp_path.rglob("manifest.json"))
    else:
        dataset.download()
        assert len(list(tmp_path.rglob("manifest.json"))) == 1
        assert dataset._local_full_name is None
    assert len(requests) == 2
    assert "/templates/gene/1_0/" in requests[1]
