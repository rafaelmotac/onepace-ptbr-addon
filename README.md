# One Pace PT-BR Subs — Stremio Addon

Stremio addon that provides **Brazilian Portuguese (PT-BR)** subtitles for [One Pace](https://onepace.net), the fan edit that removes filler from One Piece.

Works with **One Pace Addon**, **One Pace RD Premium**, and any other addon that uses One Pace episodes on Stremio.

## Install

Paste this URL in Stremio (Addons > search bar):

```
https://3715ec511f6d-onepace-ptbr-addon.baby-beamup.club/manifest.json
```

Done. PT-BR subtitles will automatically appear when watching One Pace episodes.

Each episode offers two subtitle options:
- **Portuguese** — clean SRT, compatible with any player
- **PT-BR Styled** — ASS with original formatting (signs, positioning, effects)

## Available Episodes (465 total)

| Saga | Arcs | Episodes |
|------|------|:--------:|
| East Blue | Romance Dawn, Orange Town, Syrup Village, Gaimon, Baratie, Arlong Park, Buggy's Crew, Loguetown | 38 |
| Alabasta | Reverse Mountain, Whisky Peak, Koby-Meppo, Little Garden, Drum Island, Alabasta | 39 |
| Skypiea | Jaya, Skypiea | 33 |
| Water Seven | Long Ring Long Land, Water Seven, Enies Lobby, Post-Enies Lobby | 57 |
| Thriller Bark | Thriller Bark | 22 |
| Marineford | Sabaody, Amazon Lily, Impel Down, Straw Hats Adventures, Marineford, Post-War | 52 |
| Fishman Island | Return to Sabaody, Fishman Island | 27 |
| Dressrosa | Punk Hazard, Dressrosa, Zou | 80 |
| Whole Cake Island | Whole Cake Island, Wapol's Omnivorous Hurrah, Reverie | 43 |
| Wano | Wano (Acts 1-3) | 54 |
| Egghead | Egghead | 20 |

> Subtitles sourced from [onepaceptbr](https://onepaceptbr.github.io/) community translations and the [official One Pace subtitles repo](https://github.com/one-pace/one-pace-public-subtitles).

## Run Locally

```bash
git clone https://github.com/rafaelmotac/onepace-ptbr-addon.git
cd onepace-ptbr-addon
npm install
npm start
```

The addon will be available at `http://127.0.0.1:7000/manifest.json`.

To use on your local network (e.g. TV in the living room), replace `127.0.0.1` with your machine's IP address.

## Update Subtitles

### From the official One Pace repo

```bash
git clone https://github.com/one-pace/one-pace-public-subtitles.git
npm run convert
```

### From Google Drive (onepaceptbr)

```bash
npm run download
npm run download:dry  # list only
```

## Project Structure

```
onepace-ptbr-addon/
├── index.js                     # Stremio addon (ESM)
├── package.json
├── Procfile                     # Beamup/Heroku deploy
├── logo.png                     # Addon logo
├── subs/                        # Subtitles
│   ├── mapping.json             # Episode ID -> file mapping
│   ├── RO_1.srt                 # SRT (clean text)
│   ├── RO_1.ass                 # ASS (styled)
│   └── ...
├── scripts/
│   ├── subtitle_converter.py    # Shared module
│   ├── convert_ass_to_srt.py    # Converts ASS -> SRT
│   ├── download_all_subs.py     # Downloads from Google Drive
│   └── translate_subs.py        # Translates EN -> PT-BR
└── tests/
    └── addon.test.js            # Addon tests
```

## How It Works

```
Stremio requests subtitles for episode "RO_1"
  -> addon looks up mapping.json
  -> finds RO_1.srt and RO_1.ass
  -> returns both URLs (GitHub raw)
  -> Stremio shows "Portuguese" and "PT-BR Styled" in the subtitle list
```

Subtitle files are hosted on GitHub (raw.githubusercontent.com) and the addon runs on Beamup (free Stremio hosting).

## Credits

- [One Pace](https://onepace.net) — One Piece fan edit project
- [One Pace Public Subtitles](https://github.com/one-pace/one-pace-public-subtitles) — official subtitles
- [onepaceptbr](https://onepaceptbr.github.io/) — PT-BR translation team
- [Stremio Addon SDK](https://github.com/Stremio/stremio-addon-sdk)
- [One Pace Addon](https://github.com/fedew04/OnePaceStremio) — catalog and streams for Stremio

## License

MIT
