# TV Renamer - TMDB Edition

Script Python per rinominare file di serie TV usando l'API di TheMovieDB (TMDB).

## Installazione

```bash
pip install requests
```

## Uso Base

### Metodo Semplice (usando rename.py - legge token da config.json)

#### Test (Dry Run - senza modificare i file)
```bash
python rename.py "LOST.S01E01.MKV" --dry-run
```

#### Rinomina singolo file
```bash
python rename.py "LOST.S01E01.MKV"
```

#### Rinomina tutti i file in una directory
```bash
python rename.py . --dry-run
```

#### Rinomina ricorsivamente
```bash
python rename.py . --recursive --dry-run
```

### Metodo Avanzato (specificando il token manualmente)

```bash
python tv_renamer.py "LOST.S01E01.MKV" --api-token "IL_TUO_TOKEN" --dry-run
```

## Formato Supportati

Lo script riconosce automaticamente questi formati:
- `LOST.S01E01.MKV` → Lost (1x01) Pilot (1).mkv
- `Lost.1x01.mkv` → Lost (1x01) Pilot (1).mkv  
- `Lost.101.mkv` → Lost (1x01) Pilot (1).mkv
- `The.White.Lotus.S01E01.1080p.AMZN.WEB-DL.mkv` → The White Lotus (1x01) Arrivals (1080p) (WEB-DL) (AMZN).mkv
- `Stranger.Things.S04E01.1080p.NF.WEB-DL.mkv` → Stranger Things (4x01) Episode Title (1080p) (WEB-DL) (NF).mkv
- `Ted.Lasso.S02E01.2160p.ATVP.WEB-DL.mkv` → Ted Lasso (2x01) Episode Title (2160p) (WEB-DL) (ATVP).mkv
- `The.Mandalorian.S03E01.1080p.DSNP.WEB-DL.mkv` → The Mandalorian (3x01) Episode Title (1080p) (WEB-DL) (DSNP).mkv
- `Lost.S01E02.2160p.BluRay.mkv` → Lost (1x02) Pilot (2) (2160p) (BluRay).mkv
- `Breaking.Bad.S05E01.720p.HDTV.mkv` → Breaking Bad (5x01) Live Free or Die (720p) (HDTV).mkv
- `The.Office.S02E01.1080p.WEBRip.mkv` → The Office (2x01) The Dundies (1080p) (WEBRip).mkv
- `Friends.S01E01.DVDRip.avi` → Friends (1x01) Pilot (DVDRip).avi

### Rilevamento Automatico

Lo script identifica e include automaticamente nel nome:
- **Risoluzione**: 720p, 1080p, 2160p
- **Source**: BluRay, WEB-DL, WEBRip, HDTV, DVDRip, BDRip, BRRip
- **Platform Web** (solo per WEB-DL/WEBRip): AMZN, NF, ATVP, DSNP, e altri
- **Estensione**: sempre convertita in minuscolo (.mkv, .avi, .mp4, etc.)

**Nota Platform**: Il platform viene rilevato automaticamente se presente tra la risoluzione e WEB-DL/WEBRip.
Se non presente nel file originale, non verrà aggiunto (potrai aggiungerlo manualmente dopo).

## Configurazione

Il file `mytvnamerconfig.json` controlla il formato di output.

Template predefinito:
```
%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s%(ext)s
```

Risultato:
```
Lost (1x01) Pilot Part 1.mkv
```

### Variabili disponibili:
- `%(seriesname)s` - Nome serie
- `%(seasonnumber)d` - Numero stagione
- `%(episode)s` - Numero episodio (con format 02d)
- `%(episodename)s` - Nome episodio
- `%(resolution)s` - Risoluzione (720p, 1080p, 2160p) se presente
- `%(source)s` - Source (BluRay, WEB-DL, WEBRip, HDTV, DVDRip, etc.) se presente
- `%(platform)s` - Platform web (AMZN, NF, ATVP, DSNP, etc.) se presente
- `%(ext)s` - Estensione file (sempre minuscola)

## Esempio Completo

```bash
# Test su un file senza risoluzione/source
python rename.py "LOST.S01E01.MKV" --dry-run

# Output:
# Parsed: LOST - S01E01
# Found 20 results for 'LOST':
#   1. Lost (2004) - ID: 4607
#   2. Lost (2001) - ID: 1575
#   ...
# 
# Found: Lost (S01E01)
# Episode: Pilot (1)
# 
# Old: LOST.S01E01.MKV
# New: Lost (1x01) Pilot (1).mkv
# 
# [DRY RUN - No changes made]

# Test su un file con risoluzione e source
python rename.py "The.White.Lotus.S01E01.1080p.WEB-DL.mkv" --dry-run

# Output:
# Parsed: The White Lotus - S01E01
# Resolution: 1080p
# Source: WEB-DL
#
# Found: The White Lotus (S01E01)
# Episode: Arrivals
#
# Old: The.White.Lotus.S01E01.1080p.WEB-DL.mkv
# New: The White Lotus (1x01) Arrivals (1080p) (WEB-DL).mkv

# Test su un file con risoluzione, source e platform
python rename.py "The.White.Lotus.S01E01.1080p.AMZN.WEB-DL.mkv" --dry-run

# Output:
# Parsed: The White Lotus - S01E01
# Resolution: 1080p
# Source: WEB-DL
# Platform: AMZN
#
# Found: The White Lotus (S01E01)
# Episode: Arrivals
#
# Old: The.White.Lotus.S01E01.1080p.AMZN.WEB-DL.mkv
# New: The White Lotus (1x01) Arrivals (1080p) (WEB-DL) (AMZN).mkv

# Se va bene, rimuovi --dry-run per rinominare
python rename.py "LOST.S01E01.MKV"
```

## Note

- Usa sempre `--dry-run` prima per testare
- Lo script usa il file `mytvnamerconfig.json` se presente
- Cerca automaticamente la serie su TMDB
- Supporta multiple lingue (configurabile)
- **Formato automatico**: Se risoluzione e source sono presenti nel nome file originale, vengono automaticamente inclusi nel nuovo nome
- **Platform Web**: Il platform (AMZN, NF, ATVP, DSNP, etc.) viene rilevato automaticamente se presente tra risoluzione e WEB-DL/WEBRip
- **Estensioni**: Sempre convertite in minuscolo (.mkv, .mp4, etc.)

### Platform comuni:
- **AMZN** - Amazon Prime Video
- **NF** - Netflix
- **ATVP** - Apple TV+
- **DSNP** - Disney+
- **HMAX** - HBO Max
- **HULU** - Hulu
- **PCOK** - Peacock
- **PMTP** - Paramount+

## Rinomina Speciale: Jimmy Kimmel Live

Lo script include una gestione speciale per gli show di Jimmy Kimmel Live che non richiede connessione a TMDB.

### Formato
Da: `Jimmy.Kimmel.2026.04.30.Meryl.Streep.720p.WEB.h264-EDITH`
A: `Jimmy Kimmel Live! (2026.04.30) Meryl Streep (720p) (HDTV)`

### Regole di Rinomina
- Rileva automaticamente file che iniziano con "Jimmy.Kimmel"
- Mantiene la data nel formato originale tra parentesi: `(YYYY.MM.DD)`
- Rimuove i punti dal nome dell'ospite
- Include la risoluzione: `(720p)`
- Aggiunge sempre il tag: `(HDTV)`
- Rimuove tutte le informazioni dopo "720p" (codec, gruppo release, etc.)

### Esempio
```bash
python rename.py "Jimmy.Kimmel.2026.04.30.Meryl.Streep.720p.WEB.h264-EDITH.mkv" --dry-run

# Output:
# [Jimmy Kimmel Live - Special handling]
# Date: 2026.04.30
# Guest: Meryl Streep
#
# Old: Jimmy.Kimmel.2026.04.30.Meryl.Streep.720p.WEB.h264-EDITH.mkv
# New: Jimmy Kimmel Live! (2026.04.30) Meryl Streep (720p) (HDTV).mkv
#
# [DRY RUN - No changes made]
```

## Rinomina Speciale: The Daily Show

Lo script include una gestione speciale anche per gli show di The Daily Show che non richiede connessione a TMDB.

### Formato
Da: `The.Daily.Show.2026.01.05.Mark.Kelly.720p.WEB.h264-EDITH`
A: `The Daily Show (2026.01.05) Mark Kelly (720p) (WEB-DL)`

### Regole di Rinomina
- Rileva automaticamente file che iniziano con "The.Daily.Show"
- Mantiene la data nel formato originale tra parentesi: `(YYYY.MM.DD)`
- Rimuove i punti dal nome dell'ospite
- Include la risoluzione: `(720p)`
- Aggiunge sempre il tag: `(WEB-DL)`
- Rimuove tutte le informazioni dopo "720p" (source raw, codec, gruppo release, etc.)

### Esempio
```bash
python rename.py "The.Daily.Show.2026.01.05.Mark.Kelly.720p.WEB.h264-EDITH.mkv" --dry-run

# Output:
# [The Daily Show - Special handling]
# Date: 2026.01.05
# Guest: Mark Kelly
#
# Old: The.Daily.Show.2026.01.05.Mark.Kelly.720p.WEB.h264-EDITH.mkv
# New: The Daily Show (2026.01.05) Mark Kelly (720p) (WEB-DL).mkv
#
# [DRY RUN - No changes made]
```
