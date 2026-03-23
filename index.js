import sdk from "stremio-addon-sdk";
import fs from "node:fs";
import path from "node:path";

const { addonBuilder, serveHTTP } = sdk;

const pkg = JSON.parse(
  fs.readFileSync(path.join(import.meta.dirname, "package.json"), "utf-8")
);

const SUBS_DIR = path.join(import.meta.dirname, "subs");
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
  logo: "https://onepace.net/images/one-pace-logo.svg",
  resources: [{ name: "subtitles", types: ["series"] }],
  types: ["series"],
  catalogs: [],
};

const builder = new addonBuilder(manifest);

builder.defineSubtitlesHandler(async ({ type, id, extra }) => {
  const videoID = extra?.videoID || id;

  console.log(`🔍 Request: type=${type} id=${id} videoID=${videoID}`);

  if (Object.hasOwn(subtitleMap, videoID)) {
    const srtFile = subtitleMap[videoID];
    const srtUrl = `${SUBS_BASE_URL}/${srtFile}`;

    console.log(`  ✅ ${videoID} → ${srtFile}`);

    return {
      subtitles: [
        {
          id: `onepace-ptbr-${videoID}`,
          url: srtUrl,
          lang: "por",
        },
      ],
    };
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
