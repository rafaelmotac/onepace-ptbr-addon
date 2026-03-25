# One Pace PT-BR Subs — Stremio Addon

Addon do Stremio que fornece legendas em **Portugues do Brasil (PT-BR)** para o [One Pace](https://onepace.net), o fan edit que remove fillers do One Piece.

Funciona com o **One Pace Addon**, **One Pace RD Premium** e qualquer outro addon que use os episodios do One Pace no Stremio.

## Instalar

Cole essa URL no Stremio (Addons > barra de busca):

```
https://3715ec511f6d-onepace-ptbr-addon.baby-beamup.club/manifest.json
```

Pronto. As legendas PT-BR aparecem automaticamente ao assistir episodios do One Pace.

Cada episodio oferece duas opcoes de legenda:
- **Portuguese** — SRT limpo, compativel com qualquer player
- **PT-BR (Estilizado)** — ASS com formatacao original (sinais, posicionamento, efeitos)

## Episodios Disponiveis

| Saga | Arcos | Episodios |
|------|-------|:---------:|
| East Blue | Romance Dawn, Orange Town, Syrup Village, Gaimon, Baratie, Arlong Park, Buggy's Crew, Loguetown | 38 |
| Alabasta | Reverse Mountain, Whisky Peak, Koby-Meppo, Little Garden, Drum Island, Alabasta | 39 |
| Skypiea | Jaya, Skypiea | 33 |
| Water Seven | Water Seven | 20 |
| *Em andamento* | Enies Lobby, Post War, Egghead, e mais... | +134 |

> O addon e atualizado conforme novas traducoes ficam prontas.

## Rodar Localmente

```bash
git clone https://github.com/rafaelmotac/onepace-ptbr-addon.git
cd onepace-ptbr-addon
npm install
npm start
```

O addon fica disponivel em `http://127.0.0.1:7000/manifest.json`.

Para usar na rede local (ex: TV na sala), substitua `127.0.0.1` pelo IP da maquina.

## Atualizar Legendas

### A partir do repo oficial do One Pace

```bash
# Clone o repo de legendas
git clone https://github.com/one-pace/one-pace-public-subtitles.git

# Converta ASS -> SRT
npm run convert
```

### A partir do Google Drive (onepaceptbr)

```bash
# Baixa todas as legendas do onepaceptbr.github.io
npm run download

# Ou so lista o que seria baixado
npm run download:dry
```

## Estrutura

```
onepace-ptbr-addon/
├── index.js                     # Addon Stremio (ESM)
├── package.json
├── Procfile                     # Deploy Beamup/Heroku
├── subs/                        # Legendas
│   ├── mapping.json             # Mapeamento ID -> arquivos
│   ├── RO_1.srt                 # SRT (texto limpo)
│   ├── RO_1.ass                 # ASS (estilizado)
│   └── ...
├── scripts/
│   ├── subtitle_converter.py    # Modulo compartilhado
│   ├── convert_ass_to_srt.py    # Converte ASS -> SRT
│   ├── download_all_subs.py     # Baixa do Google Drive
│   └── translate_subs.py        # Traduz EN -> PT-BR
└── tests/
    └── addon.test.js            # Testes do addon
```

## Como Funciona

```
Stremio pede legendas para o episodio "RO_1"
  -> addon consulta mapping.json
  -> encontra RO_1.srt e RO_1.ass
  -> retorna ambas as URLs (GitHub raw)
  -> Stremio exibe "Portuguese" e "PT-BR (Estilizado)" na lista de legendas
```

Os arquivos de legenda ficam hospedados no GitHub (raw.githubusercontent.com) e o addon roda no Beamup (hosting gratuito do Stremio).

## Creditos

- [One Pace](https://onepace.net) — projeto de fan edit do One Piece
- [One Pace Public Subtitles](https://github.com/one-pace/one-pace-public-subtitles) — legendas oficiais
- [onepaceptbr](https://onepaceptbr.github.io/) — equipe de traducao PT-BR
- [Stremio Addon SDK](https://github.com/Stremio/stremio-addon-sdk)
- [One Pace Addon](https://github.com/fedew04/OnePaceStremio) — catalogo e streams para Stremio

## Licenca

MIT
