#!/usr/bin/env python3
"""Small end-to-end contract test for the static corpus release generator."""

import json
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_release import build  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
corpus = {
    "meta": {"name": "Test corpus", "version": "1", "updated": "2026-07-26", "description": "fixture", "modes": ["reflection"]},
    "practices": [{
        "id": "test-practice", "title": "Test the release", "instruction": "Pause and verify the generated artefacts.",
        "notice": "A small fixture keeps this contract test independent of a second corpus copy.", "tradition": "Test",
        "discipline": "science", "mode": "reflection", "minutes": 1, "where": "anywhere",
        "source": {"rights": "cc0", "note": "Test fixture"}
    }]
}
raw = json.dumps(corpus, sort_keys=True).encode()

with tempfile.TemporaryDirectory() as temporary:
    out = Path(temporary) / "dist"
    release = build(corpus, raw, out, "0123456789abcdef", "2026-07-26T12:00:00Z")
    manifest = json.loads((out / "api/v1/manifest.json").read_text())
    index = json.loads((out / "api/v1/ambient-one/index.json").read_text())
    assert manifest["release"] == release
    assert manifest["practice_count"] == len(corpus["practices"])
    assert len(index["practices"]) == len(corpus["practices"])
    assert (out / "api/v1/practices" / "test-practice.json").is_file()
    pack = out / "releases" / release / "ambient-one" / "pack.zip"
    with zipfile.ZipFile(pack) as archive:
        assert "index.json" in archive.namelist()
        assert any(path.endswith(".bmp") for path in archive.namelist())

print("release contract OK")
