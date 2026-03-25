import sdk from "stremio-addon-sdk";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { addonBuilder, serveHTTP } = sdk;

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const pkg = JSON.parse(
  fs.readFileSync(path.join(__dirname, "package.json"), "utf-8")
);

const SUBS_DIR = path.join(__dirname, "subs");
let subtitleMap = {};

try {
  subtitleMap = JSON.parse(
    fs.readFileSync(path.join(SUBS_DIR, "mapping.json"), "utf-8")
  );
  console.log(`📂 ${Object.keys(subtitleMap).length} legendas PT-BR carregadas`);
} catch (e) {
  console.error("❌ Erro ao carregar mapping.json:", e.message);
}

const SUBS_BASE_URL =
  process.env.SUBS_BASE_URL ||
  "https://raw.githubusercontent.com/rafaelmotac/onepace-ptbr-addon/main/subs";

if (SUBS_BASE_URL.includes("SEU_USUARIO")) {
  console.warn("⚠️  SUBS_BASE_URL ainda contém 'SEU_USUARIO'. Configure a variável de ambiente SUBS_BASE_URL.");
}

const manifest = {
  id: "community.onepace.ptbr.subs",
  version: pkg.version,
  name: "One Pace PT-BR Subs",
  description:
    "Legendas em Português do Brasil para o One Pace. Baseado no repo oficial one-pace-public-subtitles.",
  logo: "https://raw.githubusercontent.com/rafaelmotac/onepace-ptbr-addon/main/logo.png",
  resources: [{ name: "subtitles", types: ["series"] }],
  types: ["series"],
  catalogs: [],
  stremioAddonsConfig: {
    issuer: "https://stremio-addons.net",
    signature: "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..Ga-TpY9kPyn3ycnmbXPddg.dXg8oEqCPgtoWcQlKN5PaPbhp1LdRk_L-0bPQ7kWUBRunYXvkqqnn_QfrHu7o9t4xB6feLuHSu-o9ABfK8iE41YEMVuHs7pM7N3LL624Eu0DbsHbdVtSSpICG0fXVlAC.Wg0yI3iOYn7v4BT8FiJXaw",
  },
};

const builder = new addonBuilder(manifest);

builder.defineSubtitlesHandler(async ({ type, id, extra }) => {
  const videoID = extra?.videoID || id;

  console.log(`🔍 Request: type=${type} id=${id} videoID=${videoID}`);

  if (Object.hasOwn(subtitleMap, videoID)) {
    const entry = subtitleMap[videoID];
    const srtFile = typeof entry === "string" ? entry : entry.srt;
    const assFile = typeof entry === "object" ? entry.ass : null;
    const subtitles = [];

    if (srtFile) {
      subtitles.push({
        id: `onepace-ptbr-${videoID}`,
        url: `${SUBS_BASE_URL}/${srtFile}`,
        lang: "por",
      });
    }

    if (assFile) {
      subtitles.push({
        id: `onepace-ptbr-styled-${videoID}`,
        url: `${SUBS_BASE_URL}/${assFile}`,
        lang: "por",
        title: "PT-BR (Estilizado)",
      });
    }

    console.log(`  ✅ ${videoID} → ${subtitles.length} opções`);

    return { subtitles };
  }

  return { subtitles: [] };
});

const PORT = process.env.PORT || 7000;
let server;

serveHTTP(builder.getInterface(), { port: PORT })
  .then((srv) => {
    server = srv;
    console.log(`\n🏴‍☠️ One Pace PT-BR Subs Addon`);
    console.log(`   Manifest: http://127.0.0.1:${PORT}/manifest.json`);
    console.log(`\n📋 ${Object.keys(subtitleMap).length} episódios com legenda PT-BR:`);
    Object.keys(subtitleMap).sort().forEach((id) => console.log(`   • ${id}`));
    console.log(`\n💡 Instale no Stremio: http://127.0.0.1:${PORT}/manifest.json\n`);
  })
  .catch((err) => {
    console.error(`❌ Falha ao iniciar servidor na porta ${PORT}:`, err.message);
    process.exit(1);
  });

const shutdown = () => {
  console.log("\n🛑 Encerrando servidor...");
  if (server?.server) {
    server.server.close(() => process.exit(0));
  } else {
    process.exit(0);
  }
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
