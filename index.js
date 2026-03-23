const { addonBuilder, serveHTTP } = require("stremio-addon-sdk");
const fs = require("fs");
const path = require("path");

// ============================================================
//  One Pace PT-BR Subtitles Addon para Stremio
//  Fornece legendas em Português do Brasil para o One Pace
// ============================================================

const SUBS_DIR = path.join(__dirname, "subs");
let subtitleMap = {};

try {
  const mapping = JSON.parse(
    fs.readFileSync(path.join(SUBS_DIR, "mapping.json"), "utf-8")
  );
  subtitleMap = mapping;
  console.log(`📂 ${Object.keys(subtitleMap).length} legendas PT-BR carregadas`);
} catch (e) {
  console.error("❌ Erro ao carregar mapping.json:", e.message);
}

// URL base onde os SRTs estão hospedados no GitHub
// MUDE para o seu repositório!
const SUBS_BASE_URL =
  process.env.SUBS_BASE_URL ||
  "https://raw.githubusercontent.com/SEU_USUARIO/onepace-ptbr-subs/main/subs";

// ---------- Manifest ----------
const manifest = {
  id: "community.onepace.ptbr.subs",
  version: "1.0.0",
  name: "One Pace PT-BR Subs",
  description:
    "Legendas em Português do Brasil para o One Pace. Baseado no repo oficial one-pace-public-subtitles.",
  logo: "https://onepace.net/images/one-pace-logo.svg",
  resources: [
    {
      name: "subtitles",
      types: ["series"],
    },
  ],
  types: ["series"],
  catalogs: [],
};

const builder = new addonBuilder(manifest);

// ---------- Subtitle Handler ----------
builder.defineSubtitlesHandler(({ type, id, extra }) => {
  const videoID = extra?.videoID || id;

  console.log(`🔍 Request: type=${type} id=${id} videoID=${videoID}`);

  if (subtitleMap[videoID]) {
    const srtFile = subtitleMap[videoID];
    const srtUrl = `${SUBS_BASE_URL}/${srtFile}`;

    console.log(`  ✅ ${videoID} → ${srtFile}`);

    return Promise.resolve({
      subtitles: [
        {
          id: `onepace-ptbr-${videoID}`,
          url: srtUrl,
          lang: "por",
        },
      ],
    });
  }

  return Promise.resolve({ subtitles: [] });
});

// ---------- Start ----------
const PORT = process.env.PORT || 7000;
serveHTTP(builder.getInterface(), { port: PORT });

console.log(`\n🏴‍☠️ One Pace PT-BR Subs Addon`);
console.log(`   Manifest: http://127.0.0.1:${PORT}/manifest.json`);
console.log(`\n📋 ${Object.keys(subtitleMap).length} episódios com legenda PT-BR:`);
Object.keys(subtitleMap).sort().forEach((id) => console.log(`   • ${id}`));
console.log(`\n💡 Instale no Stremio: http://127.0.0.1:${PORT}/manifest.json\n`);
