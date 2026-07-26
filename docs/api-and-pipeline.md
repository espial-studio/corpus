# Corpus API

corpus.espial.studio is a public, read-only delivery surface for the Espial
Corpus. It is designed for people, applications, and devices to read a stable,
attributed collection of attention practices.

## API v1

| Endpoint | Meaning | Cache policy |
| --- | --- | --- |
| /api/v1/manifest.json | Current release, source commit, corpus checksum, and resource links | 60 seconds |
| /api/v1/practices.json | Complete published corpus | 5 minutes |
| /api/v1/practices/{id}.json | One published practice | 5 minutes |
| /api/v1/ambient-one/manifest.json | Current device format and release information | 5 minutes |
| /api/v1/ambient-one/index.json | Compact device catalogue, card links, and hashes | 5 minutes |
| /releases/{release}/... | Immutable canonical JSON, cards, and pack archive | one year, immutable |

All API and release responses carry Access-Control-Allow-Origin: *. No endpoint
accepts writes, authentication, user identity, or personalised ordering.

## Published data

Each release is generated from one reviewed corpus snapshot. The generator
rejects malformed records, duplicate IDs, unsupported quotations, and
incomplete cultural provenance.

The complete practice document and individual practice records are
authoritative. Ambient One indexes and card documents are derived convenience
formats. They retain source and cultural provenance fields even where a small
device screen cannot display all of them.

## Releases

Release paths are immutable. The stable API paths point to the current release;
the manifest links both forms so consumers can choose freshness or a pinned
version. A failed build never changes the previously served release.

There are no device-instigated or scheduled public releases.

## Local release build

The release generator takes a published corpus JSON snapshot as input:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python scripts/build_release.py \
      --input /path/to/published-corpus.json \
      --out dist \
      --source-commit local-test

The generated dist directory is intentionally ignored by git.
