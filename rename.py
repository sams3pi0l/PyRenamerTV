#!/usr/bin/env python3
"""
Wrapper semplificato per tv_renamer.py
Legge le credenziali da config.json
"""

import sys
import json
import subprocess
from pathlib import Path


def load_config():
    """Carica config.json"""
    config_file = Path(__file__).parent / "config.json"
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Errore: config.json non trovato!")
        print("Crea un file config.json con il tuo TMDB API token")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Uso: python rename.py <file o directory> [opzioni]")
        print("\nEsempi:")
        print("  python rename.py LOST.S01E01.MKV --dry-run")
        print("  python rename.py . --dry-run")
        print("  python rename.py . --recursive")
        sys.exit(1)
    
    # Carica configurazione
    config = load_config()
    api_token = config.get('tmdb_api_token')
    
    if not api_token:
        print("Errore: tmdb_api_token non trovato in config.json")
        sys.exit(1)
    
    # Costruisci comando
    python_exe = sys.executable
    script_dir = Path(__file__).parent
    tv_renamer = script_dir / "tv_renamer.py"
    
    cmd = [python_exe, str(tv_renamer)] + sys.argv[1:] + ["--api-token", api_token]
    
    # Esegui
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
