#!/usr/bin/env python3
"""
Converte arquivos ASS em português do repo one-pace-public-subtitles para SRT,
mapeando cada arquivo para o ID de episódio usado pelo Stremio.

Uso:
  python convert-ass-to-srt.py <caminho-do-repo-one-pace-public-subtitles> <pasta-de-saida>

Exemplo:
  python convert-ass-to-srt.py ../one-pace-public-subtitles ./subs
"""

import os
import re
import sys
import json

# Mapeamento: nome do arco no filesystem → prefixo do ID no Stremio
ARC_TO_PREFIX = {
    "romancedawn": "RO",
    "orangetown": "OR",
    "syrupvillage": "SY",
    "gaimon": "GA",
    "baratie": "BA",
    "arlongpark": "AR",
    "loguetown": "LO",
    "reversemountain": "RM",
    "whiskypeak": "WH",
    "littlegarden": "LI",
    "drumisland": "DI",
    "alabasta": "AL",
    "jaya": "JA",
    "skypiea": "SK",
    "longringlongland": "LR",
    "waterseven": "WS",
    "enieslobby": "EN",
    "thrillerbark": "TB",
    "sabaody": "SAB",
    "amazonlily": "AM",
    "impeldown": "IM",
    "marineford": "MA",
    "fishmanisland": "FI",
    "punkhazard": "PH",
    "dressrosa": "DR",
    "zou": "ZO",
    "wholecakeisland": "WC",
    "reverie": "REV",
    "wano": "WA",
    "egghead": "EH",
}

# Mapeamento alternativo para nomes no Final Subs (com espaços)
FINAL_SUBS_ARC_MAP = {
    "Romance Dawn": "RO",
    "Orange Town": "OR",
    "Syrup Village": "SY",
    "Gaimon": "GA",
    "Baratie": "BA",
    "Arlong Park": "AR",
    "Loguetown": "LO",
    "Reverse Mountain": "RM",
    "Whisky Peak": "WH",
    "Whiskey Peak": "WH",
    "Little Garden": "LI",
    "Drum Island": "DI",
    "Alabasta": "AL",
    "Jaya": "JA",
    "Skypiea": "SK",
    "Long Ring Long Land": "LR",
    "Water Seven": "WS",
    "Enies Lobby": "EN",
    "Thriller Bark": "TB",
    "Sabaody": "SAB",
    "Amazon Lily": "AM",
    "Impel Down": "IM",
    "Marineford": "MA",
    "Fishman Island": "FI",
    "Punk Hazard": "PH",
    "Dressrosa": "DR",
    "Zou": "ZO",
    "Whole Cake Island": "WC",
    "Reverie": "REV",
    "Wano": "WA",
    "Egghead": "EH",
}


def ass_to_srt(ass_content):
    """Converte conteúdo ASS para SRT, removendo tags de formatação."""
    lines = ass_content.split('\n')
    events_section = False
    format_line = None
    dialogues = []

    for line in lines:
        line = line.strip()
        if line == '[Events]':
            events_section = True
            continue
        if events_section and line.startswith('Format:'):
            format_line = [f.strip() for f in line[7:].split(',')]
            continue
        if events_section and line.startswith('Dialogue:'):
            if format_line:
                parts = line[10:].split(',', len(format_line) - 1)
                if len(parts) == len(format_line):
                    entry = dict(zip(format_line, parts))
                    # Pular linhas de signs/songs/karaoke
                    style = entry.get('Style', '').lower()
                    if any(s in style for s in ['sign', 'song', 'op ', 'ed ', 'karaoke', 'title']):
                        continue
                    dialogues.append(entry)

    srt_lines = []
    counter = 1
    for d in dialogues:
        start = d.get('Start', '0:00:00.00')
        end = d.get('End', '0:00:00.00')
        text = d.get('Text', '')

        # Remover tags ASS como {\an8}, {\pos(x,y)}, {\fad(x,y)}, etc.
        text = re.sub(r'\{[^}]*\}', '', text)
        # Converter \N e \n para quebra de linha
        text = text.replace('\\N', '\n').replace('\\n', '\n')
        text = text.strip()

        if not text:
            continue

        # Converter formato de tempo: 0:00:00.00 → 00:00:00,000
        def convert_time(t):
            match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', t)
            if match:
                h, m, s, cs = match.groups()
                return f"{int(h):02d}:{m}:{s},{cs}0"
            return t

        srt_lines.append(str(counter))
        srt_lines.append(f"{convert_time(start)} --> {convert_time(end)}")
        srt_lines.append(text)
        srt_lines.append('')
        counter += 1

    return '\n'.join(srt_lines)


def find_and_convert(repo_path, output_dir):
    """Encontra todos os arquivos ptbr.ass e Portugues.ass e converte para SRT."""
    os.makedirs(output_dir, exist_ok=True)
    converted = {}

    # Fonte 1: Arquivos individuais (ptbr.ass) nas pastas dos episódios
    main_dir = os.path.join(repo_path, 'main')
    for root, dirs, files in os.walk(main_dir):
        for f in files:
            if f.endswith('ptbr.ass') and 'Other' not in root:
                filepath = os.path.join(root, f)
                # Extrair nome do arco e número do episódio
                # Ex: "romancedawn 01 ptbr.ass" → arc="romancedawn", ep=1
                match = re.match(r'(\w+)\s+(\d+)\s+ptbr\.ass', f)
                if match:
                    arc_name = match.group(1).lower()
                    ep_num = int(match.group(2))
                    prefix = ARC_TO_PREFIX.get(arc_name)
                    if prefix:
                        episode_id = f"{prefix}_{ep_num}"
                        if episode_id not in converted:
                            converted[episode_id] = filepath

    # Fonte 2: Final Subs (Portugues.ass) - sobrescreve se existir
    final_subs = os.path.join(repo_path, 'main', 'Release', 'Final Subs')
    if os.path.exists(final_subs):
        for f in os.listdir(final_subs):
            if 'Portugues' in f and f.endswith('.ass'):
                filepath = os.path.join(final_subs, f)
                # Ex: "[One Pace][1] Romance Dawn 01 [1080p] Portugues.ass"
                match = re.search(r'\]\s+(.+?)\s+(\d+)\s+\[', f)
                if match:
                    arc_name = match.group(1)
                    ep_num = int(match.group(2))
                    prefix = FINAL_SUBS_ARC_MAP.get(arc_name)
                    if prefix:
                        episode_id = f"{prefix}_{ep_num}"
                        converted[episode_id] = filepath

    # Converter todos
    mapping = {}
    for episode_id, ass_path in sorted(converted.items()):
        try:
            with open(ass_path, 'r', encoding='utf-8-sig') as fh:
                ass_content = fh.read()
            srt_content = ass_to_srt(ass_content)
            srt_filename = f"{episode_id}.srt"
            srt_path = os.path.join(output_dir, srt_filename)
            with open(srt_path, 'w', encoding='utf-8') as fh:
                fh.write(srt_content)
            mapping[episode_id] = srt_filename
            print(f"  ✅ {episode_id} → {srt_filename} (de {os.path.basename(ass_path)})")
        except Exception as e:
            print(f"  ❌ {episode_id}: {e}")

    # Salvar mapeamento
    mapping_path = os.path.join(output_dir, 'mapping.json')
    with open(mapping_path, 'w') as fh:
        json.dump(mapping, fh, indent=2)
    print(f"\n📄 Mapeamento salvo em {mapping_path}")
    print(f"📊 Total: {len(mapping)} episódios convertidos")

    return mapping


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    repo_path = sys.argv[1]
    output_dir = sys.argv[2]

    print("🔄 Convertendo legendas ASS → SRT...\n")
    find_and_convert(repo_path, output_dir)
