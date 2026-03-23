#!/usr/bin/env python3
"""
Translate English ASS subtitle files to Brazilian Portuguese using Claude API.

Preserves all ASS formatting, timing, and styles — only translates dialogue text.

Usage:
  python translate_subs.py <input_dir> <output_dir>
  python translate_subs.py downloads/en_subs downloads/ptbr_subs

Requires:
  ANTHROPIC_API_KEY environment variable
  pip install anthropic
"""

import argparse
import os
import re
import sys
import time

import anthropic


def extract_dialogues(ass_content: str) -> tuple[list[str], list[dict]]:
    """Parse ASS file and extract dialogue entries with their text."""
    lines = ass_content.split("\n")
    result_lines: list[str] = []
    dialogues: list[dict] = []
    events_section = False
    format_fields: list[str] | None = None

    for line in lines:
        stripped = line.rstrip("\r")

        if stripped.strip() == "[Events]":
            events_section = True
            result_lines.append(stripped)
            continue

        if stripped.strip().startswith("[") and stripped.strip().endswith("]") and events_section:
            events_section = False
            result_lines.append(stripped)
            continue

        if events_section and stripped.strip().startswith("Format:"):
            format_fields = [f.strip() for f in stripped.strip()[7:].split(",")]
            result_lines.append(stripped)
            continue

        if events_section and stripped.strip().startswith("Dialogue:") and format_fields:
            parts = stripped.strip()[10:].split(",", len(format_fields) - 1)
            if len(parts) == len(format_fields):
                entry = dict(zip(format_fields, parts))
                style = entry.get("Style", "").lower()

                skip_styles = [
                    "sign", "song", "op ", "ed ", "karaoke",
                    "title", "chapter", "credit", "eyecatch",
                    "next ep", "preview",
                ]
                should_skip = any(s in style for s in skip_styles)

                text = entry.get("Text", "")
                # Strip ASS tags to get plain text for translation check
                plain = re.sub(r"\{[^}]*\}", "", text).replace("\\N", " ").replace("\\n", " ").strip()

                dialogue_idx = len(result_lines)
                result_lines.append(stripped)

                if not should_skip and plain:
                    dialogues.append({
                        "index": dialogue_idx,
                        "full_line": stripped,
                        "text": text,
                        "plain": plain,
                        "entry": entry,
                        "format_fields": format_fields,
                        "prefix": stripped.strip()[:10],  # "Dialogue: "
                    })
                continue

        result_lines.append(stripped)

    return result_lines, dialogues


def build_translation_prompt(dialogues: list[dict]) -> str:
    """Build a prompt with numbered lines for batch translation."""
    lines = []
    for i, d in enumerate(dialogues):
        lines.append(f"[{i}] {d['plain']}")
    return "\n".join(lines)


def parse_translation_response(response: str, count: int) -> dict[int, str]:
    """Parse numbered translation response back to a dict."""
    translations: dict[int, str] = {}
    for line in response.strip().split("\n"):
        match = re.match(r"\[(\d+)\]\s*(.*)", line)
        if match:
            idx = int(match.group(1))
            text = match.group(2).strip()
            if idx < count and text:
                translations[idx] = text
    return translations


def apply_translations(
    dialogues: list[dict],
    translations: dict[int, str],
    result_lines: list[str],
) -> list[str]:
    """Apply translated text back into the ASS dialogue lines."""
    for i, d in enumerate(dialogues):
        if i not in translations:
            continue

        translated = translations[i]
        original_text = d["text"]

        # Preserve leading ASS tags (like {\an8}, {\pos(x,y)}, etc.)
        leading_tags = ""
        tag_match = re.match(r"^(\{[^}]*\})+", original_text)
        if tag_match:
            leading_tags = tag_match.group(0)

        # Replace \N in translation with ASS newline
        translated = translated.replace("\n", "\\N")

        new_text = leading_tags + translated

        # Rebuild the dialogue line
        entry = d["entry"]
        fields = d["format_fields"]
        entry["Text"] = new_text
        values = [entry[f] for f in fields]
        new_line = "Dialogue: " + ",".join(values)
        result_lines[d["index"]] = new_line

    return result_lines


def translate_batch(
    client: anthropic.Anthropic,
    dialogues: list[dict],
    filename: str,
) -> dict[int, str]:
    """Send dialogues to Claude for translation in batches."""
    all_translations: dict[int, str] = {}
    batch_size = 80

    for start in range(0, len(dialogues), batch_size):
        batch = dialogues[start : start + batch_size]
        prompt_text = build_translation_prompt(batch)

        print(f"    Traduzindo linhas {start+1}-{start+len(batch)} de {len(dialogues)}...")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""Translate the following anime subtitle lines from English to Brazilian Portuguese (PT-BR).

Rules:
- Keep the [number] prefix exactly as-is
- Use natural, colloquial Brazilian Portuguese (not Portugal Portuguese)
- Keep character names unchanged (Luffy, Zoro, Nami, Usopp, Sanji, etc.)
- Keep attack names in their known forms (Gomu Gomu no, Santoryu, etc.)
- Preserve the tone and emotion of each line
- If a line has multiple sentences, translate them all
- Do NOT add or remove lines
- One translated line per [number]

File: {filename}

{prompt_text}""",
                }
            ],
        )

        batch_translations = parse_translation_response(
            response.content[0].text, len(batch)
        )

        for local_idx, text in batch_translations.items():
            all_translations[start + local_idx] = text

        # Rate limit
        if start + batch_size < len(dialogues):
            time.sleep(1)

    return all_translations


def translate_file(client: anthropic.Anthropic, input_path: str, output_path: str) -> bool:
    """Translate a single ASS file from EN to PT-BR."""
    print(f"  {os.path.basename(input_path)}")

    content = None
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(input_path, encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if not content:
        print(f"    Erro: nao consegui ler o arquivo")
        return False

    result_lines, dialogues = extract_dialogues(content)

    if not dialogues:
        print(f"    Sem dialogos para traduzir")
        return False

    print(f"    {len(dialogues)} linhas de dialogo")

    translations = translate_batch(client, dialogues, os.path.basename(input_path))
    print(f"    {len(translations)}/{len(dialogues)} linhas traduzidas")

    result_lines = apply_translations(dialogues, translations, result_lines)

    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(result_lines))

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate English ASS subtitles to PT-BR using Claude API"
    )
    parser.add_argument("input_dir", help="Directory with English .ass files")
    parser.add_argument("output_dir", help="Output directory for PT-BR .ass files")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Erro: diretorio nao encontrado: {args.input_dir}")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Erro: ANTHROPIC_API_KEY nao definida")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    os.makedirs(args.output_dir, exist_ok=True)

    ass_files = sorted(f for f in os.listdir(args.input_dir) if f.endswith("_en.ass"))

    if not ass_files:
        print("Nenhum arquivo _en.ass encontrado")
        sys.exit(1)

    print(f"Traduzindo {len(ass_files)} arquivos EN -> PT-BR\n")

    success = 0
    for filename in ass_files:
        input_path = os.path.join(args.input_dir, filename)
        output_name = filename.replace("_en.ass", "_ptbr.ass")
        output_path = os.path.join(args.output_dir, output_name)

        if translate_file(client, input_path, output_path):
            success += 1

    print(f"\nPronto! {success}/{len(ass_files)} arquivos traduzidos")
    print(f"Saida: {args.output_dir}/")


if __name__ == "__main__":
    main()
