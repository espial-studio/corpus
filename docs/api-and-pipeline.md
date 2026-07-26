# Corpus API and release pipeline

`corpus.espial.studio` is a public, read-only delivery surface. Loom is the editor and the only normal publisher; the device has no credentials and no write path.

## API v1

| Endpoint | Meaning | Cache policy |
| --- | --- | --- |
| `/api/v1/manifest.json` | Current release, source Loom commit, corpus checksum and resource links | 60 seconds |
| `/api/v1/practices.json` | Full lossless published corpus | 5 minutes |
| `/api/v1/practices/{id}.json` | One full published practice | 5 minutes |
| `/api/v1/ambient-one/manifest.json` | Current device format and release information | 5 minutes |
| `/api/v1/ambient-one/index.json` | Compact device catalogue, card links and hashes | 5 minutes |
| `/releases/{release}/…` | Immutable canonical JSON, cards and pack archive | one year, immutable |

All API/release responses carry `Access-Control-Allow-Origin: *`. No endpoint accepts writes, authentication, user identity, or personalised ordering.

## Published data rules

`data/practices.json` at the pinned Loom commit is the only editorial input. The generator refuses malformed records, duplicate IDs, a quote on a `method-only` source, and incomplete cultural provenance. The API is therefore never generated from Loom drafts or Durable Object state.

The full `practices.json` and every per-practice document remain authoritative. The Ambient One index and `card.json` projections are derived convenience formats. Each carries `requires_attribution`, and the full card JSON retains the source and cultural provenance fields even when a small BMP cannot display all of them.

## Release sequence

```text
Curator presses Publish in Loom
  → Loom commits validated data/practices.json
  → Loom's Durable Object sends repository_dispatch for that exact commit SHA
  → corpus Action checks out that SHA, builds static assets, deploys atomically
  → current v1 manifest points to the immutable release
```

There are no scheduled, quiescence, or device-instigated commits. A failed public deployment does not change the Loom commit; rerun the corpus workflow with the same SHA to retry it.

## One-time setup

1. Install the existing Loom GitHub App on both `espial-studio/loom` and `espial-studio/corpus` (the same organisation installation can be expanded to include both repositories).
2. Give the app **Contents: read and write** permission. Loom mints one short-lived installation token after a curator publishes: it writes to Loom and asks the corpus repository to release that exact new commit.
3. In the **corpus** repository Actions secrets, add `LOOM_READER_APP_ID`, `LOOM_READER_PRIVATE_KEY`, `CLOUDFLARE_API_TOKEN`, and `CLOUDFLARE_ACCOUNT_ID`. No GitHub Actions secrets are needed in Loom for this handoff.
4. Ensure the Cloudflare token can edit Workers and DNS for the `espial.studio` zone. Deploy once with `npx wrangler deploy`; it provisions `corpus.espial.studio` as a Workers Custom Domain if no conflicting DNS record exists.
5. Use **Run workflow** in the corpus repository's **Build and deploy corpus release** Action with a known-good Loom commit to confirm the initial release. Subsequent releases are requested directly by a curator publish in Loom.

If the GitHub App is not installed on `corpus`, Loom still completes the
repository publish. The Pending page records that the public-release handoff
needs attention instead of calling the curator publish a failure.

## Local release check

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_release.py \
  --input ../loom/data/practices.json \
  --out dist \
  --source-commit local-test
```

The release output is intentionally ignored by git. It is reproducible from a source commit and deployed directly by the release workflow.
