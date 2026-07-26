#!/usr/bin/env python3
"""Build a complete, static public corpus release from one pinned editorial snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import textwrap
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, MARGIN = 480, 800, 38


def font_path(*candidates: str) -> str:
    """Use the intended macOS faces locally and a pinned Linux fallback in CI."""
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError(f"no usable font found; checked: {', '.join(candidates)}")


SERIF = font_path(
    "/System/Library/Fonts/Supplemental/PTSerif.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
)
SANS = font_path(
    "/System/Library/Fonts/Supplemental/PTSans.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def validate(corpus: dict) -> None:
    if not isinstance(corpus.get("meta"), dict) or not isinstance(corpus.get("practices"), list):
        raise ValueError("corpus must contain meta and practices")
    seen: set[str] = set()
    for practice in corpus["practices"]:
        required = ("id", "title", "instruction", "notice", "tradition", "mode", "minutes", "source")
        if not isinstance(practice, dict) or any(not practice.get(key) for key in required):
            raise ValueError(f"malformed practice: {practice!r}")
        if practice["id"] in seen:
            raise ValueError(f"duplicate practice id: {practice['id']}")
        seen.add(practice["id"])
        rights = practice["source"].get("rights")
        if rights not in {"public-domain", "cc0", "method-only"}:
            raise ValueError(f"invalid rights for {practice['id']}")
        if rights == "method-only" and practice.get("quote"):
            raise ValueError(f"method-only practice cannot include a quote: {practice['id']}")
        provenance = ("peoples", "shared_by", "permission_basis")
        if any(practice.get(key) for key in provenance) and not (practice.get("peoples") and practice.get("permission_basis")):
            raise ValueError(f"incomplete cultural provenance: {practice['id']}")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrapped(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.replace("\n", " ").split():
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=face) <= width:
            current = candidate
        elif current:
            lines.append(current)
            current = word
        else:
            lines.append(word[:30] + "…")
            current = ""
    if current:
        lines.append(current)
    return lines


def draw_lines(draw: ImageDraw.ImageDraw, y: int, lines: list[str], face: ImageFont.FreeTypeFont, leading: int) -> int:
    height = face.getbbox("Ag")[3] - face.getbbox("Ag")[1]
    for line in lines:
        draw.text((MARGIN, y), line, fill=0, font=face)
        y += height + leading
    return y


def render_card(practice: dict, output: Path) -> None:
    """A compact card; the lossless card.json always accompanies this display export."""
    image = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(image)
    available = WIDTH - MARGIN * 2
    instruction = practice["instruction"]
    if len(instruction) > 500:
        instruction = textwrap.shorten(instruction, width=500, placeholder=" …")
    for title_size, instruction_size in ((34, 20), (31, 19), (28, 18), (25, 17), (23, 16)):
        title_face, body_face = font(SERIF, title_size), font(SANS, instruction_size)
        kicker_face, footer_face = font(SANS, 13), font(SANS, 11)
        title_lines = wrapped(draw, practice["title"], title_face, available)
        body_lines = wrapped(draw, instruction, body_face, available)
        attribution = practice.get("peoples") or practice["tradition"]
        attribution_lines = wrapped(draw, f"Held by: {attribution}", kicker_face, available)
        line_height = lambda face: face.getbbox("Ag")[3] - face.getbbox("Ag")[1]
        total = (len(title_lines) * (line_height(title_face) + 5) + len(body_lines) * (line_height(body_face) + 6) + len(attribution_lines) * (line_height(kicker_face) + 2) + 124)
        if total <= HEIGHT - MARGIN * 2:
            break
    else:
        raise ValueError(f"cannot fit card: {practice['id']}")
    y = MARGIN
    draw.text((MARGIN, y), f"{practice['tradition']} · {practice['minutes']} MIN", fill=0, font=kicker_face)
    y += 38
    y = draw_lines(draw, y, title_lines, title_face, 5) + 18
    y = draw_lines(draw, y, body_lines, body_face, 6) + 14
    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=0, width=1)
    y += 11
    draw_lines(draw, y, attribution_lines, kicker_face, 2)
    draw.text((MARGIN, HEIGHT - MARGIN), "ESPIAL CORPUS · AMBIENT ONE", fill=0, font=footer_face)
    draw.text((WIDTH - MARGIN - 72, HEIGHT - MARGIN), practice["id"][:12], fill=0, font=footer_face)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="BMP")


def card_projection(practice: dict, release: str) -> dict:
    attribution = {key: practice[key] for key in ("peoples", "shared_by", "permission_basis") if practice.get(key)}
    return {
        "format": 1,
        "release": release,
        "id": practice["id"],
        "title": practice["title"],
        "instruction": practice["instruction"],
        "notice": practice["notice"],
        "quote": practice.get("quote"),
        "tradition": practice["tradition"],
        "discipline": practice["discipline"],
        "mode": practice["mode"],
        "minutes": practice["minutes"],
        "where": practice["where"],
        "source": practice["source"],
        "attribution": attribution,
        "requires_attribution": bool(attribution),
        "content_sha256": digest(json.dumps(practice, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    }


def build(corpus: dict, raw: bytes, out: Path, source_commit: str, published_at: str) -> str:
    validate(corpus)
    meta = corpus["meta"]
    release = f"{meta['updated']}.{source_commit[:12]}.v1"
    release_root = out / "releases" / release
    api_root = out / "api" / "v1"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "site", out)

    canonical_sha = digest(raw)
    cards: list[dict] = []
    for practice in corpus["practices"]:
        card = card_projection(practice, release)
        practice_path = f"/releases/{release}/practices/{practice['id']}.json"
        card_path = f"/releases/{release}/ambient-one/cards/{practice['id']}.bmp"
        card["asset"] = card_path
        write_json(release_root / "practices" / f"{practice['id']}.json", practice)
        write_json(release_root / "ambient-one" / "cards" / f"{practice['id']}.json", card)
        render_card(practice, release_root / "ambient-one" / "cards" / f"{practice['id']}.bmp")
        cards.append({
            "id": card["id"], "title": card["title"], "tradition": card["tradition"], "mode": card["mode"],
            "minutes": card["minutes"], "asset": card_path, "card": f"/releases/{release}/ambient-one/cards/{practice['id']}.json",
            "content_sha256": card["content_sha256"], "requires_attribution": card["requires_attribution"]
        })

    index = {"format": 1, "release": release, "practices": cards}
    ambient_manifest = {"format": 1, "release": release, "card_format": "bmp-1bit-xteink-x3-480x800", "count": len(cards), "index": "/api/v1/ambient-one/index.json"}
    manifest = {
        "api_version": "v1", "schema_version": 1, "release": release, "published_at": published_at,
        "source_commit": source_commit, "corpus_sha256": canonical_sha, "practice_count": len(cards),
        "resources": {
            "practices": "/api/v1/practices.json", "ambient_one": "/api/v1/ambient-one/manifest.json",
            "release": f"/releases/{release}/manifest.json"
        }
    }
    release_manifest = {**manifest, "resources": {**manifest["resources"], "ambient_one_index": f"/releases/{release}/ambient-one/index.json"}}
    write_json(release_root / "manifest.json", release_manifest)
    write_json(release_root / "practices.json", corpus)
    write_json(release_root / "ambient-one" / "index.json", index)
    write_json(release_root / "ambient-one" / "manifest.json", ambient_manifest)
    write_json(api_root / "manifest.json", manifest)
    write_json(api_root / "practices.json", corpus)
    write_json(api_root / "ambient-one" / "index.json", index)
    write_json(api_root / "ambient-one" / "manifest.json", ambient_manifest)
    for practice in corpus["practices"]:
        write_json(api_root / "practices" / f"{practice['id']}.json", practice)

    archive = release_root / "ambient-one" / "pack.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as pack:
        for path in sorted((release_root / "ambient-one").rglob("*")):
            if path.is_file() and path != archive:
                pack.write(path, path.relative_to(release_root / "ambient-one"))
    return release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--published-at", default=None)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    corpus = json.loads(raw)
    published_at = args.published_at or f"{corpus['meta']['updated']}T00:00:00Z"
    release = build(corpus, raw, args.out, args.source_commit, published_at)
    print(release)


if __name__ == "__main__":
    main()
