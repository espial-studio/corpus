# Espial corpus release service

This directory is the deployable public API at `corpus.espial.studio`. It has
no editorial corpus copy: the release action reads one pinned commit from
`espial-studio/loom`, generates static API and Ambient One assets, and deploys
them directly. See [the API and pipeline guide](docs/api-and-pipeline.md).

The `practices.json`, `build.py`, and `index.html` files currently present in
this local directory are a superseded pre-Loom viewer kept only for reference;
they are explicitly ignored and are not part of the new public service.

## Local release build

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_release.py \
  --input ../curation-tool/data/practices.json \
  --out dist \
  --source-commit local-test
```

## Legacy viewer notes

A cross-disciplinary corpus of attention practices. `practices.json` is the
canonical source; everything else is generated from it.

```
practices.json   the corpus (canonical, hand-edited)
build.py         reads the JSON, emits the viewer
index.html       generated — self-contained, open it directly in a browser
```

Rebuild after editing the corpus:

```bash
python3 corpus/build.py
```

The viewer embeds the corpus rather than fetching it, deliberately: a
`file://` page cannot fetch a sibling JSON (CORS), and artifact hosting
blocks external requests. One canonical source, one double-clickable output.

## Rights position

This is the part to keep honest as the corpus grows.

**Copyright protects expression, not methods.** A practice or technique is not
copyrightable; a particular author's wording of it is. So:

- Every `instruction` and `notice` field is **original prose written for this
  corpus**. No source's wording is reproduced, including from sources that are
  still in copyright.
- Direct quotation appears **only** in the optional `quote` field, and **only**
  from works verified as public domain or CC0, always with attribution.

`source.rights` accepts exactly three values:

| Value | Meaning | May quote? |
|---|---|---|
| `public-domain` | Published 1930 or earlier (US 95-year term), or otherwise verified | Yes |
| `cc0` | Explicit public domain dedication | Yes |
| `method-only` | The method is described in original prose because methods are not copyrightable ([17 U.S.C. §102(b)](https://www.law.cornell.edu/uscode/text/17/102)). Used where the source is a **living tradition** rather than a fixed text, or a **modern work whose expression is still in copyright** | **Never** |

`method-only` exists to be honest about provenance, not to widen what may be
reproduced. `build.py` refuses to build if a `method-only` entry carries a
quote, and the viewer labels those cards *"method described, not reproduced"*
rather than passing them off as public domain.

Public domain here means published 1930 or earlier (US, 95-year term) or
otherwise verified. **Translations carry their own copyright** — this is the
easiest mistake to make. Marcus Aurelius is ancient, but Gregory Hays' 2002
translation is not; George Long's 1862 translation is.

### Deliberately excluded

| Source | Why |
|---|---|
| Oblique Strategies (Eno & Schmidt, 1975) | In copyright |
| Zen Flesh, Zen Bones (Reps, 1957) | In copyright. The Vijñāna Bhairava techniques it popularised are described here in original prose from the ancient source instead |
| Thanissaro Bhikkhu translations | "Free distribution" is not an open licence — Sujato's CC0 used instead |
| Ñāṇamoli's Visuddhimagga, Nicolaïdes, Betty Edwards, Hays' Meditations, MBSR material | All in copyright |

## Cultural provenance position

Separate from copyright, and stricter. **Copyright status does not settle
whether cultural knowledge may be used.** [Indigenous Cultural and Intellectual
Property](https://www.artslaw.com.au/information-sheet/indigenous-cultural-intellectual-property-icip-aitb/)
guidance is explicit that permission comes from the originating community
according to its own protocols, *regardless of public availability or
public-domain status*.

Rules for this corpus:

1. Include only knowledge the holding community has **deliberately and publicly
   shared** for others to take up, or general philosophical concepts openly
   discussed in public life by that community.
2. **Never** include ceremonial, initiatory, sacred-restricted or secret material.
3. **Name the peoples** the knowledge belongs to. Attribution is part of the
   practice and must not be stripped in any rendered format — `build.py`
   enforces this by refusing to render a `peoples` entry without displaying it.
4. Where a named Elder or holder shared it, name them and record why in
   `permission_basis`.
5. Describe in original prose; never reproduce the holder's wording.
6. **Where permission basis cannot be established, leave it out.** A thinner
   corpus is the correct outcome.

Age is not consent. Much nineteenth and early-twentieth-century ethnography is
public domain by age but was collected under colonial conditions without
consent, so **this corpus does not draw practices from colonial ethnographic
records.**

Thirteen entries currently carry provenance fields. Each names its people and
records why inclusion is appropriate:

| Entry | People | Basis |
|---|---|---|
| `dadirri` | Ngan'gikurunggurr and Ngen'giwumirri | Presented to the world by Dr Miriam-Rose Ungunmerr-Baumann AM from 1988, explicitly as a gift |
| `wayfinding` | Pacific Islander navigating peoples, Satawal | Mau Piailug chose to teach beyond his island as the tradition was being lost; Polynesian Voyaging Society teaches publicly |
| `whare-tapa-wha` | Māori | Published by Sir Mason Durie in 1984 expressly for use across the NZ health system |
| `aajiiqatigiinniq`, `avatittinnik-kamatsiarniq` | Inuit of Nunavut | Inuit Qaujimajatuqangit principles, formally adopted as public governance framework |
| `sumak-kawsay` | Quechua and Aymara | Enshrined in the Ecuadorian (2008) and Bolivian (2009) constitutions |
| `tri-hita-karana` | Balinese | Openly promoted by Balinese institutions; UNESCO-recognised subak system |
| `seven-generations` | Haudenosaunee | Governance principle long discussed publicly by Haudenosaunee representatives |
| `sankofa` | Akan | Proverb and adinkra symbol in open public use |
| `harambee` | Communities of Kenya | National principle, on the coat of arms |
| `ubuntu` | Nguni | Extensively discussed in published African philosophy |
| `ayni`, `minga` | Quechua, Aymara and Andean | Openly documented communal practices |

**Where the standard could not be met, nothing was added.** Circumpolar
material beyond the publicly promulgated Inuit Qaujimajatuqangit principles was
left out, because the available sources are colonial-era ethnography. Hawaiian
*hoʻoponopono* was excluded as family and ceremonial practice that has already
been badly distorted commercially. Yoruba *Ifá* was excluded as initiatory.

### Notable sources

- **[SuttaCentral](https://suttacentral.net)** — Bhikkhu Sujato's complete Pali
  Canon translations, dedicated to the public domain under **CC0**. Explicitly
  produced to be free of copyright, which makes it the single best open source
  for contemplative material.
- **Project Gutenberg / Wikisource / Internet Archive** — for the pre-1930
  editions cited in `source`.

## Schema

One object per practice in `practices.practices[]`:

| Field | Notes |
|---|---|
| `id` | stable kebab-case identifier |
| `title` | short imperative or noun phrase |
| `instruction` | the practice itself, original prose |
| `notice` | what to watch for, or why it works |
| `quote` | optional `{text, attribution}`, PD/CC0 only |
| `peoples` | optional — community the knowledge belongs to; forces attribution on render |
| `shared_by` | optional — named holder who shared it publicly |
| `permission_basis` | optional — why inclusion is appropriate |
| `tradition` | lineage or school |
| `discipline` | contemplative, philosophy, art, science, psychology, literature |
| `mode` | concentration, awareness, perception, inquiry, reflection |
| `minutes` | approximate duration |
| `where` | context it can be run in |
| `source` | bibliographic record including `rights` |

## Current coverage

110 practices across 90 traditions.

- **By discipline** — contemplative 41, philosophy 30, science 15, art 10,
  psychology 7, literature 7
- **By mode** — reflection 31, perception 24, concentration 21, inquiry 20,
  awareness 14
- **By rights** — public domain 89, method-only 12, CC0 9

**Regions and traditions represented:** early Buddhism (CC0 Pali Canon), Sōtō
Zen, Japanese aesthetics and craft (ma, ichigo ichie, mono no aware, Bashō,
Musashi, kintsugi, kata, shinrin-yoku), Taoism, Confucianism and
Neo-Confucianism, Wang Yangming, Song landscape painting, Chinese internal
arts, Chinese strategic thought, the Yijing, Upanishadic Vedanta, classical
yoga, Hatha yoga, Kashmir Shaivism, Jainism, Bhakti and Kabir, the Gita,
Ayurveda, Ngan'gikurunggurr and Ngen'giwumirri, Haudenosaunee, Nguni, Quechua
and Aymara, Sufism, Islamic contemplative practice and geometric design, Mussar
and Breslov Hasidism, Jewish practice, Stoicism, Pyrrhonism, the Socratic
method, baroque moralism, Montaigne, Ignatian and Benedictine and Carmelite and
apophatic Christianity, Ruskin, Goethe, Leonardo, atelier drawing, Agassiz,
Grinnell, Darwin, Faraday, Poincaré, Humboldt, Cajal, Peirce, William James,
Thoreau, Hopkins and Dorothy Wordsworth.

**Added in the second expansion:** Korean Seon, nunchi and Toegye's *gyeong*;
canonical walking meditation, Burmese noting and Balinese Tri Hita Karana;
Pacific wayfinding and Te Whare Tapa Whā; Akan *sankofa*, Kenyan *harambee* and
the ancient Egyptian declarations before Ma'at; two Inuit Qaujimajatuqangit
principles; *sumak kawsay* and *minga*.

**Women's voices**, previously the corpus's worst structural gap, now include
Julian of Norwich, Teresa of Ávila, Hildegard of Bingen, Sei Shōnagon, Sor Juana
Inés de la Cruz, Rābiʿa al-ʿAdawiyya, Mirabai, Florence Nightingale, Ida B.
Wells, Caroline Herschel and Simone Weil — alongside Dorothy Wordsworth from the
first pass. This gap is structural in the public-domain record rather than
accidental, so it needs deliberate effort to close and is not yet closed.

**Gaps remaining:** Sámi and other circumpolar traditions outside the published
Inuit principles; Aboriginal and Torres Strait Islander knowledge beyond
dadirri; Melanesian and Micronesian beyond wayfinding; Indigenous North
American beyond the Haudenosaunee governance principle; Central Asian; Roma.
Each needs a verifiable permission basis, and a public-domain source alone does
not supply one.
