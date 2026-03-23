# 🏴‍☠️ One Pace PT-BR Subs — Addon Stremio

Addon do Stremio que fornece legendas em **Português do Brasil** para os episódios do [One Pace](https://onepace.net).

As legendas são extraídas do [repositório oficial de legendas do One Pace](https://github.com/one-pace/one-pace-public-subtitles), convertidas de ASS para SRT, e servidas como addon de legendas para o Stremio.

## 📋 Episódios disponíveis

| Arco            | IDs        | Episódios |
|-----------------|------------|-----------|
| Romance Dawn    | RO_1–RO_4 | 4         |
| Orange Town     | OR_1–OR_3 | 3         |
| Syrup Village   | SY_1–SY_7 | 6 (falta SY_2) |
| Gaimon          | GA_1       | 1         |
| **Total**       |            | **14**    |

> Conforme a equipe portuguesa do One Pace traduz mais arcos, basta rodar o script de conversão novamente para atualizar.

## 🚀 Setup rápido

### 1. Clonar e instalar

```bash
git clone https://github.com/SEU_USUARIO/onepace-ptbr-subs.git
cd onepace-ptbr-subs
npm install
```

### 2. Configurar a URL dos SRTs

Edite a variável `SUBS_BASE_URL` no `index.js` para apontar pro seu repositório GitHub:

```
https://raw.githubusercontent.com/SEU_USUARIO/onepace-ptbr-subs/main/subs
```

Ou defina via variável de ambiente:

```bash
export SUBS_BASE_URL="https://raw.githubusercontent.com/SEU_USUARIO/onepace-ptbr-subs/main/subs"
```

### 3. Rodar o addon

```bash
npm start
```

O addon estará disponível em `http://127.0.0.1:7000/manifest.json`.

### 4. Instalar no Stremio

1. Abra o Stremio
2. Vá em **Addons** → cole a URL do manifest
3. Instale o addon
4. Ao assistir um episódio do One Pace, as legendas PT-BR aparecerão automaticamente na lista de legendas!

## 🔄 Atualizar legendas

Para converter novas legendas quando a equipe pt-BR traduzir mais arcos:

```bash
# Clone o repo oficial de legendas (se ainda não tiver)
git clone https://github.com/one-pace/one-pace-public-subtitles.git

# Rode o script de conversão
python3 scripts/convert-ass-to-srt.py ./one-pace-public-subtitles ./subs
```

## 🌐 Deploy (opcional)

### GitHub Pages (estático — sem servidor)

Se preferir não rodar um servidor, hospede os SRTs no GitHub e crie um addon estático. Os arquivos SRT já estão na pasta `subs/` e podem ser acessados via `raw.githubusercontent.com`.

### Vercel / Railway

O addon funciona em qualquer plataforma que rode Node.js. Basta fazer deploy e ajustar a `SUBS_BASE_URL`.

## 🏗️ Como funciona

```
Stremio → pede legendas para episódio "RO_1"
       → addon verifica mapping.json
       → encontra "RO_1.srt"
       → retorna URL do SRT no GitHub
       → Stremio exibe a legenda "Português" na lista
```

## 📁 Estrutura

```
onepace-ptbr-subs/
├── index.js                    # Addon Stremio
├── package.json
├── subs/                       # Legendas SRT convertidas
│   ├── mapping.json            # Mapeamento ID → arquivo
│   ├── RO_1.srt
│   ├── RO_2.srt
│   └── ...
├── scripts/
│   └── convert-ass-to-srt.py   # Converte ASS → SRT
└── README.md
```

## 🙏 Créditos

- [One Pace](https://onepace.net) — projeto de fan edit
- [One Pace Public Subtitles](https://github.com/one-pace/one-pace-public-subtitles) — legendas oficiais
- Equipe de tradução pt-BR do One Pace
- [Stremio Addon SDK](https://github.com/Stremio/stremio-addon-sdk)
