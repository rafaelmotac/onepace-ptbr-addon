#!/usr/bin/env python3
"""
=============================================================
 One Pace PT-BR — Download e Conversão Automática de Legendas
=============================================================

Este script:
1. Baixa TODAS as legendas pt-BR das pastas do Google Drive
   listadas no site onepaceptbr.github.io
2. Converte ASS/SSA → SRT (se necessário)
3. Mapeia cada arquivo pro ID do episódio no Stremio
4. Gera o mapping.json final pro addon

Requisitos:
  pip install gdown

Uso:
  python3 download-all-subs.py

  # Ou especificando pasta de saída:
  python3 download-all-subs.py --output ./subs

  # Só listar o que seria baixado (dry run):
  python3 download-all-subs.py --dry-run
"""

import os
import re
import sys
import json
import glob
import shutil
import argparse
import subprocess
from pathlib import Path

# ============================================================
#  MAPEAMENTO COMPLETO: Arco → Prefixo de ID no Stremio
# ============================================================
ARC_PREFIX = {
    "Romance Dawn":         "RO",
    "Orange Town":          "OR",
    "Syrup Village":        "SY",
    "Gaimon":               "GA",
    "Baratie":              "BA",
    "Arlong Park":          "AR",
    "Buggy's Crew":         "BUGGYS_CREW",
    "Loguetown":            "LO",
    "Reverse Mountain":     "RM",
    "Whisky Peak":          "WH",
    "Koby-Meppo":           "COVER_KOBYMEPPO",
    "Little Garden":        "LI",
    "Drum Island":          "DI",
    "Alabasta":             "AL",
    "Jaya":                 "JA",
    "Skypiea":              "SK",
    "Long Ring Long Land":  "LR",
    "Water Seven":          "WS",
    "Enies Lobby":          "EN",
    "Post-Enies Lobby":     "PEN",
    "Thriller Bark":        "TB",
    "Sabaody":              "SAB",
    "Amazon Lily":          "AM",
    "Impel Down":           "IM",
    "Straw Hats Adventures":"COVER_SHSS",
    "Marineford":           "MA",
    "Post-War":             "PW",
    "Return to Sabaody":    "RTS",
    "Fishman Island":       "FI",
    "Punk Hazard":          "PH",
    "Dressrosa":            "DR",
    "Zou":                  "ZO",
    "Whole Cake Island":    "WC",
    "Reverie":              "REV",
    "Wano":                 "WA",
    "Egghead":              "EH",
}

# ============================================================
#  PASTAS DO GOOGLE DRIVE — extraídas do onepaceptbr.github.io
# ============================================================
GDRIVE_FOLDERS = [
    # East Blue
    ("Buggy's Crew",         "1N7SX80QdYA3RmiB9a0Gv0CcVO5U-W42T"),
    ("Loguetown",            "1kGtlrg_yDQhmk90hzgKJkEJyHG8dE0Bm"),
    # Arabasta saga
    ("Reverse Mountain",     "19Y27qgR7sQM7xcaeQVT5p_utRZhEMwv-"),
    ("Whisky Peak",          "1-0aNZMiCfiabU7lItI9hnUw9tDDvGNUi"),
    ("Koby-Meppo",           "1-1HHj1J1GyOJB-0s0tYFulXZ3Edih2dA"),
    ("Little Garden",        "1-38c5xnM21BsE4gPF-AUOBKo5sRje1gA"),
    ("Drum Island",          "1-394JF2Js6SLOfA5_xzZF8rMUbXuxuew"),
    ("Alabasta",             "1-CHXA4WOhu-NcFXo3zlb8IHZRcLjmKa9"),
    # Skypiea saga
    ("Jaya",                 "1-DbtZkM4ZQryu6ddZ_jSg-I0mkA0ZmJ9"),
    ("Skypiea",              "1-PQqH_ck_vLSrvvRlcS94t7sTEGDjecW"),
    # Water Seven saga
    ("Long Ring Long Land",  "1-ReUSBrY2JuIkVoH900AHZvimo88INMs"),
    ("Water Seven",          "1-RyaFfPEpcTMXoob8vD8LMTTHHjV0oFX"),
    ("Enies Lobby",          "1-Y0wp4cby90m3zFLHDsZbUYEKaIQiksG"),
    ("Post-Enies Lobby",     "1-ZntQeVbCs7XY8Abe3g-yfvYSV_TP5vp"),
    # Thriller Bark
    ("Thriller Bark",        "1-boleMHeog-R1t81Kf-ApXH629m7j2xR"),
    # Marineford saga
    ("Sabaody",              "1-elhWG655zJKUEpTdh25LsbnlQ-Rx7NG"),
    ("Amazon Lily",          "1-i8blh_fRWjag4B_gySYmK0aABIES1HG"),
    ("Impel Down",           "1-ktbonZpkWu3MDnHCUaaMQp45CgvWO4t"),
    ("Straw Hats Adventures","1019fNv55FqIAG7GU4rsxJM_62HVKr9S4"),
    ("Marineford",           "105LxQOh3l58DS_MgB_i5onaRNcQheNrY"),
    ("Post-War",             "10928v4_qkWERla3eHFsq7c3wIk43-XGj"),
    # Fishman Island saga
    ("Return to Sabaody",    "10DDgiuLpGFH_nHTCYJmoFWKbOXPvwVhN"),
    ("Fishman Island",       "10Rha6Tz0VguhV_rOvJ8MjGrap6zsy7tj"),
    # Dressrosa saga
    ("Punk Hazard",          "10T3VDRRZv6PtXqi9CIWmOyJjWoEOfRbT"),
    ("Dressrosa",            "10TqoScXsXwEdKKsWAPTVoVFRwF1ry_qD"),
    # Whole Cake saga
    ("Zou",                  "10Wh5vds63c9jyehohgb5nsnG0DLOW6cc"),
    ("Whole Cake Island",    "10aU7oDKch2exbCA_TAAWHi48V_BR2h35"),
    ("Reverie",              "10h8tbsKhH_SDCzpq1E2KMLKHKU1DvzFC"),
    # Wano
    ("Wano",                 "10rAsSYTRuEea234r2q5I_z7nA1ZpDz8_"),
    # Final saga
    ("Egghead",              "10xFDV_4BjggDKJuEixYvR6i3Kk1_xnE6"),
]


# ============================================================
#  CONVERSÃO ASS → SRT
# ============================================================
def ass_to_srt(ass_content: str) -> str:
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
        if line.startswith('[') and line.endswith(']') and events_section:
            events_section = False
            continue
        if events_section and line.startswith('Format:'):
            format_line = [f.strip() for f in line[7:].split(',')]
            continue
        if events_section and line.startswith('Dialogue:'):
            if format_line:
                parts = line[10:].split(',', len(format_line) - 1)
                if len(parts) == len(format_line):
                    entry = dict(zip(format_line, parts))
                    style = entry.get('Style', '').lower()
                    # Pular signs, songs, karaoke, títulos
                    skip_styles = ['sign', 'song', 'op ', 'ed ', 'karaoke',
                                   'title', 'chapter', 'credit', 'eyecatch',
                                   'next ep', 'preview']
                    if any(s in style for s in skip_styles):
                        continue
                    dialogues.append(entry)

    srt_lines = []
    counter = 1
    for d in dialogues:
        start = d.get('Start', '0:00:00.00')
        end = d.get('End', '0:00:00.00')
        text = d.get('Text', '')

        # Remover tags ASS
        text = re.sub(r'\{[^}]*\}', '', text)
        text = text.replace('\\N', '\n').replace('\\n', '\n')
        text = text.strip()

        if not text:
            continue

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


def convert_file_to_srt(input_path: str, output_path: str) -> bool:
    """Converte um arquivo ASS/SSA para SRT. Retorna True se sucesso."""
    ext = Path(input_path).suffix.lower()

    if ext == '.srt':
        # Já é SRT, só copia
        shutil.copy2(input_path, output_path)
        return True

    if ext in ('.ass', '.ssa'):
        try:
            # Tentar vários encodings
            content = None
            for enc in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(input_path, 'r', encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if not content:
                print(f"    ⚠️  Não consegui ler {input_path}")
                return False

            srt = ass_to_srt(content)
            if srt.strip():
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(srt)
                return True
            else:
                print(f"    ⚠️  SRT vazio para {input_path}")
                return False
        except Exception as e:
            print(f"    ❌ Erro convertendo {input_path}: {e}")
            return False

    print(f"    ⚠️  Formato não suportado: {ext}")
    return False


# ============================================================
#  EXTRAÇÃO DE NÚMERO DO EPISÓDIO DO NOME DO ARQUIVO
# ============================================================
def extract_episode_number(filename: str) -> int | None:
    """
    Tenta extrair o número do episódio do nome do arquivo.
    Exemplos:
      "Romance Dawn 01.ass" → 1
      "[One Pace] Alabasta 15 PTBR.ass" → 15
      "Ep 03 - Something.srt" → 3
      "wano_22_ptbr.ass" → 22
      "01.ass" → 1
    """
    name = Path(filename).stem

    # Padrões comuns (do mais específico pro mais genérico)
    patterns = [
        r'(?:ep(?:isode)?[\s._-]*)(\d+)',     # ep01, episode 01
        r'[\s._-](\d{1,3})[\s._-]*(?:ptbr|pt-br|pt|portugues)?$',  # "nome 01 ptbr"
        r'[\s._-](\d{1,3})[\s._-]',           # "nome 01 algo"
        r'(\d{1,3})[\s._-]*(?:ptbr|pt-br|pt|portugues)',  # "01ptbr"
        r'^(\d{1,3})$',                         # "01"
        r'(\d{1,3})',                           # último recurso: qualquer número
    ]

    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            # Sanity check: episódio deve ser entre 1 e 999
            if 1 <= num <= 999:
                return num

    return None


# ============================================================
#  DOWNLOAD DO GOOGLE DRIVE
# ============================================================
def download_gdrive_folder(folder_id: str, output_dir: str) -> bool:
    """Baixa uma pasta do Google Drive usando gdown."""
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    os.makedirs(output_dir, exist_ok=True)

    try:
        result = subprocess.run(
            ["gdown", "--folder", "--remaining-ok", url, "-O", output_dir],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            # Tentar método alternativo
            result = subprocess.run(
                ["gdown", "--folder", url, "-O", output_dir, "--fuzzy"],
                capture_output=True, text=True, timeout=300
            )
        return True
    except FileNotFoundError:
        print("  ❌ gdown não encontrado! Instale com: pip install gdown")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout ao baixar pasta {folder_id}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


# ============================================================
#  PIPELINE PRINCIPAL
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Baixa e converte legendas PT-BR do One Pace para o addon Stremio"
    )
    parser.add_argument(
        "--output", "-o", default="./subs",
        help="Pasta de saída para os SRTs (default: ./subs)"
    )
    parser.add_argument(
        "--download-dir", "-d", default="./downloads",
        help="Pasta temporária para downloads do GDrive (default: ./downloads)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Só mostra o que seria feito, sem baixar"
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Pula o download e só converte arquivos já baixados"
    )
    parser.add_argument(
        "--arcs", nargs="*",
        help="Baixar apenas arcos específicos (ex: --arcs Alabasta Wano)"
    )
    args = parser.parse_args()

    output_dir = args.output
    download_dir = args.download_dir
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(download_dir, exist_ok=True)

    print("=" * 60)
    print("  One Pace PT-BR — Download & Conversão de Legendas")
    print("=" * 60)
    print(f"  Download dir: {download_dir}")
    print(f"  Output dir:   {output_dir}")
    print(f"  Arcos:        {len(GDRIVE_FOLDERS)} pastas mapeadas")
    print("=" * 60)

    if args.dry_run:
        print("\n🔍 DRY RUN — nada será baixado\n")
        for arc_name, folder_id in GDRIVE_FOLDERS:
            prefix = ARC_PREFIX.get(arc_name, "???")
            print(f"  📁 {arc_name:25s} → {prefix}_* | GDrive: {folder_id}")
        print(f"\n  Total: {len(GDRIVE_FOLDERS)} pastas")
        return

    # ---- FASE 1: Download ----
    if not args.skip_download:
        print("\n📥 FASE 1: Baixando legendas do Google Drive...\n")

        for arc_name, folder_id in GDRIVE_FOLDERS:
            if args.arcs and arc_name not in args.arcs:
                continue

            arc_dir = os.path.join(download_dir, arc_name.replace(" ", "_"))
            print(f"  📁 {arc_name}...")

            if os.path.exists(arc_dir) and os.listdir(arc_dir):
                files = os.listdir(arc_dir)
                print(f"     Já existe ({len(files)} arquivos), pulando download")
                continue

            success = download_gdrive_folder(folder_id, arc_dir)
            if success:
                files = []
                for root, dirs, fnames in os.walk(arc_dir):
                    files.extend(fnames)
                print(f"     ✅ {len(files)} arquivos baixados")
            else:
                print(f"     ⚠️  Falha no download")
    else:
        print("\n⏭️  Pulando download (--skip-download)\n")

    # ---- FASE 2: Conversão ----
    print("\n🔄 FASE 2: Convertendo e mapeando legendas...\n")

    mapping = {}

    # Carregar mapping existente se houver
    mapping_path = os.path.join(output_dir, "mapping.json")
    if os.path.exists(mapping_path):
        with open(mapping_path) as f:
            mapping = json.load(f)
        print(f"  📄 Mapping existente carregado: {len(mapping)} episódios\n")

    for arc_name, folder_id in GDRIVE_FOLDERS:
        if args.arcs and arc_name not in args.arcs:
            continue

        prefix = ARC_PREFIX.get(arc_name)
        if not prefix:
            print(f"  ⚠️  Sem prefixo para '{arc_name}', pulando")
            continue

        arc_dir = os.path.join(download_dir, arc_name.replace(" ", "_"))
        if not os.path.exists(arc_dir):
            continue

        # Encontrar todos os arquivos de legenda na pasta (recursivo)
        sub_files = []
        for ext in ['*.ass', '*.ssa', '*.srt', '*.ASS', '*.SSA', '*.SRT']:
            for root, dirs, files in os.walk(arc_dir):
                for f in files:
                    if f.lower().endswith(ext.replace('*', '').lower()):
                        sub_files.append(os.path.join(root, f))

        if not sub_files:
            print(f"  📁 {arc_name}: nenhum arquivo de legenda encontrado")
            continue

        print(f"  📁 {arc_name} ({prefix}_*): {len(sub_files)} arquivos")

        # Se só tem 1 arquivo e o arco só tem 1 episódio
        if len(sub_files) == 1:
            ep_num = extract_episode_number(sub_files[0])
            if ep_num is None:
                ep_num = 1  # Assume ep 1 se só tem 1 arquivo
            episode_id = f"{prefix}_{ep_num}"
            srt_path = os.path.join(output_dir, f"{episode_id}.srt")

            if convert_file_to_srt(sub_files[0], srt_path):
                mapping[episode_id] = f"{episode_id}.srt"
                print(f"     ✅ {episode_id} ← {Path(sub_files[0]).name}")
            continue

        # Múltiplos arquivos: extrair número de cada um
        for sub_file in sorted(sub_files):
            ep_num = extract_episode_number(sub_file)
            if ep_num is None:
                print(f"     ⚠️  Não consegui extrair episódio de: {Path(sub_file).name}")
                continue

            episode_id = f"{prefix}_{ep_num}"
            srt_path = os.path.join(output_dir, f"{episode_id}.srt")

            if convert_file_to_srt(sub_file, srt_path):
                mapping[episode_id] = f"{episode_id}.srt"
                print(f"     ✅ {episode_id} ← {Path(sub_file).name}")

    # ---- FASE 3: Salvar mapping ----
    print(f"\n💾 FASE 3: Salvando mapping.json...\n")

    # Ordenar por prefixo e número
    def sort_key(episode_id):
        parts = episode_id.rsplit('_', 1)
        prefix = parts[0]
        num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return (prefix, num)

    sorted_mapping = dict(sorted(mapping.items(), key=lambda x: sort_key(x[0])))

    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_mapping, f, indent=2, ensure_ascii=False)

    print(f"  📊 Total: {len(sorted_mapping)} episódios mapeados")
    print(f"  📄 Salvo em: {mapping_path}")

    # Resumo por arco
    print(f"\n{'='*60}")
    print("  RESUMO POR ARCO")
    print(f"{'='*60}")
    arc_counts = {}
    for ep_id in sorted_mapping:
        prefix = ep_id.rsplit('_', 1)[0]
        arc_counts[prefix] = arc_counts.get(prefix, 0) + 1

    # Inverter ARC_PREFIX pra mostrar o nome
    prefix_to_name = {v: k for k, v in ARC_PREFIX.items()}
    for prefix, count in sorted(arc_counts.items(),
                                  key=lambda x: list(ARC_PREFIX.values()).index(x[0])
                                  if x[0] in ARC_PREFIX.values() else 999):
        name = prefix_to_name.get(prefix, prefix)
        print(f"  {name:25s} ({prefix:15s}): {count:3d} eps")

    print(f"\n  {'TOTAL':25s} {'':15s}: {len(sorted_mapping):3d} eps")
    print(f"{'='*60}")
    print("\n✅ Pronto! Agora é só rodar o addon:")
    print("   npm start\n")


if __name__ == '__main__':
    main()
