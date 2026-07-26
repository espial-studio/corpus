# Espial Corpus

The Espial Corpus is a public collection of practices for attention: small,
carefully attributed invitations to notice, make, inquire, reflect, and spend
time differently.

It exists to make a broad repertoire of human ways of paying attention
available as a durable public resource. Each practice is concise enough to use
in the course of a day, but retains the source context and attribution needed
to meet it responsibly. The corpus can be read directly, used by an
application, or carried onto an Ambient One device.

**Explore the live corpus:** [corpus.espial.studio](https://corpus.espial.studio) ·
[API manifest](https://corpus.espial.studio/api/v1/manifest.json) ·
[practices](https://corpus.espial.studio/api/v1/practices.json)

## What is here

This repository contains the public delivery service for the corpus:

- a read-only, versioned JSON API;
- individual practice records with source and attribution data;
- immutable release archives;
- a compact Ambient One catalogue, card metadata, BMP sleep-screen cards, and
  downloadable card packs.

It does **not** contain the private editorial workspace or unpublished work.
Every public release is built from a reviewed source snapshot and is
independently cacheable and reproducible from its recorded commit identifier.

## Using the API

Start with the manifest:

    https://corpus.espial.studio/api/v1/manifest.json

It identifies the current release and links to the complete corpus, individual
practice records, and device-oriented resources. The API is public,
read-only, and carries permissive CORS headers. Release paths are immutable;
the stable API paths always point to the current release.

For the endpoint list, cache behaviour, and release format, see
[the API guide](docs/api-and-pipeline.md).

## Care and attribution

The corpus is not a claim that every practice is interchangeable or detached
from its history. Practice text is written for this collection; quotations are
included only where the source permits them. Source records travel with the
data, and cultural provenance fields are retained in both the API and
device-oriented formats.

The collection includes only material that can be shared responsibly in a
public corpus. Where that standard cannot be met, it is not included.

## Repository layout

| Path | Purpose |
| --- | --- |
| src/ | Cloudflare Worker serving the public API and static release assets |
| scripts/build_release.py | Deterministic release generator |
| site/ | Small public landing page |
| docs/api-and-pipeline.md | API contract and maintainer deployment notes |
| .github/workflows/release.yml | Build and deploy workflow |

## Local release build

The release generator takes a published corpus JSON snapshot as input:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python scripts/build_release.py \
      --input /path/to/published-corpus.json \
      --out dist \
      --source-commit local-test

The dist directory is generated output and is intentionally not committed.
