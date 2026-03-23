import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";

const SUBS_DIR = path.join(import.meta.dirname, "..", "subs");
const SUBS_BASE_URL =
  "https://raw.githubusercontent.com/rafaelmotac/onepace-ptbr-addon/main/subs";

describe("mapping.json", () => {
  const mapping = JSON.parse(
    fs.readFileSync(path.join(SUBS_DIR, "mapping.json"), "utf-8"),
  );

  it("loads with at least one entry", () => {
    expect(Object.keys(mapping).length).toBeGreaterThan(0);
  });

  it("has valid episode ID format", () => {
    for (const key of Object.keys(mapping)) {
      expect(key).toMatch(/^[A-Z_]+_\d+$/);
    }
  });

  it("has .srt filenames as values", () => {
    for (const value of Object.values(mapping)) {
      expect(value).toMatch(/\.srt$/);
    }
  });

  it("references existing SRT files", () => {
    for (const srtFile of Object.values(mapping)) {
      const fullPath = path.join(SUBS_DIR, srtFile);
      expect(fs.existsSync(fullPath), `Missing: ${srtFile}`).toBe(true);
    }
  });
});

describe("subtitle handler logic", () => {
  const mapping = JSON.parse(
    fs.readFileSync(path.join(SUBS_DIR, "mapping.json"), "utf-8"),
  );

  function getSubtitles(videoID) {
    if (Object.hasOwn(mapping, videoID)) {
      const srtFile = mapping[videoID];
      return [
        {
          id: `onepace-ptbr-${videoID}`,
          url: `${SUBS_BASE_URL}/${srtFile}`,
          lang: "por",
        },
      ];
    }
    return [];
  }

  it("returns subtitle for known episode", () => {
    const result = getSubtitles("RO_1");
    expect(result).toHaveLength(1);
    expect(result[0].lang).toBe("por");
    expect(result[0].url).toContain("RO_1.srt");
  });

  it("returns empty for unknown episode", () => {
    expect(getSubtitles("NONEXISTENT_999")).toEqual([]);
  });

  it("builds correct URL", () => {
    const result = getSubtitles("RO_1");
    expect(result[0].url).toBe(`${SUBS_BASE_URL}/RO_1.srt`);
  });
});
