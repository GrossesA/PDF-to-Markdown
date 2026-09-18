#!/usr/bin/env python3
"""
PDF -> Markdown mit automatischer Tool-Wahl.

Precheck analysiert jedes PDF und entscheidet (in dieser Reihenfolge):
  - Scan (kaum extrahierbarer Text)  -> Docling (mit OCR)
  - Foliensatz (Querformat)          -> Docling (saubere Struktur, Kopf-/Fusszeilen weg)
  - viele Tabellen                   -> Docling (beste Tabellenqualitaet)
  - nativer Text, simples Layout     -> pymupdf4llm (schnell)

Aufruf:
  python pdf2md.py datei1.pdf [datei2.pdf ...]
  python pdf2md.py datei.pdf --out "C:\\Ziel\\Ordner"
  python pdf2md.py datei.pdf --tool docling      (Tool erzwingen)
"""

import argparse
import sys
from pathlib import Path

# ==================== Einstellungen ====================
# Anteil der Seiten mit Tabellen, ab dem Docling gewaehlt wird (0.20 = 20 %)
TABELLEN_SEITEN_SCHWELLE = 0.20
# Anteil der Seiten mit echtem Text, darunter gilt das PDF als Scan
TEXT_ANTEIL_SCHWELLE = 0.80
# Anteil der Seiten im Querformat, ab dem das PDF als Foliensatz gilt
# und Docling gewaehlt wird (0.50 = 50 %). Hintergrund (Test 16.09.2026,
# 359-Seiten-Vorlesungsskript): pymupdf4llm liefert bei Folien flache
# Ueberschriften, Kopf-/Fusszeilen auf jeder Folie und zerlegte T-Konten;
# Docling entfernt Kopf-/Fusszeilen und baut Tabellen und Listen sauber,
# braucht auf CPU aber ca. 7,5 s pro Seite. Auf 0 setzen = Regel aus.
QUERFORMAT_SCHWELLE = 0.50
# =======================================================

import pymupdf  # kommt automatisch mit pymupdf4llm


def analysiere_pdf(pfad: Path) -> dict:
    """Sammelt Kennzahlen fuer die Tool-Entscheidung."""
    doc = pymupdf.open(pfad)
    n = len(doc)
    text_seiten = 0
    tabellen_seiten = 0
    quer_seiten = 0
    for page in doc:
        # page.rect beruecksichtigt die Seitenrotation bereits
        if page.rect.width > page.rect.height:
            quer_seiten += 1
        if len(page.get_text().strip()) > 50:
            text_seiten += 1
            if page.find_tables().tables:
                tabellen_seiten += 1
    doc.close()
    return {
        "seiten": n,
        "text_anteil": text_seiten / n if n else 0.0,
        "tabellen_anteil": tabellen_seiten / n if n else 0.0,
        "quer_anteil": quer_seiten / n if n else 0.0,
    }


def waehle_tool(info: dict) -> tuple[str, str]:
    """Gibt (tool, begruendung) zurueck."""
    if info["text_anteil"] < TEXT_ANTEIL_SCHWELLE:
        return "docling", "Scan erkannt, OCR noetig"
    if QUERFORMAT_SCHWELLE and info["quer_anteil"] >= QUERFORMAT_SCHWELLE:
        return "docling", (f"Foliensatz erkannt, Querformat auf "
                           f"{info['quer_anteil']:.0%} der Seiten")
    if info["tabellen_anteil"] >= TABELLEN_SEITEN_SCHWELLE:
        return "docling", f"Tabellen auf {info['tabellen_anteil']:.0%} der Seiten"
    return "pymupdf4llm", "nativer Text, simples Layout"


def konvertiere_pymupdf4llm(pfad: Path) -> str:
    import pymupdf4llm
    return pymupdf4llm.to_markdown(str(pfad))


def konvertiere_docling(pfad: Path) -> str:
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    ergebnis = converter.convert(str(pfad))
    return ergebnis.document.export_to_markdown()


def freier_name(ziel: Path) -> Path:
    """skript.md -> skript_2.md falls schon vorhanden."""
    if not ziel.exists():
        return ziel
    i = 2
    while True:
        kandidat = ziel.with_stem(f"{ziel.stem}_{i}")
        if not kandidat.exists():
            return kandidat
        i += 1


def verarbeite(pdf: Path, ausgabe_ordner: Path | None = None,
               tool: str = "auto") -> Path:
    """Konvertiert ein PDF und gibt den Pfad der Markdown-Datei zurueck."""
    pdf = pdf.resolve()
    if not pdf.exists():
        raise FileNotFoundError(f"Nicht gefunden: {pdf}")

    if tool == "auto":
        info = analysiere_pdf(pdf)
        tool, grund = waehle_tool(info)
        print(f"[{pdf.name}] {info['seiten']} Seiten | Text: "
              f"{info['text_anteil']:.0%} | Tabellen-Seiten: "
              f"{info['tabellen_anteil']:.0%} | Querformat: "
              f"{info['quer_anteil']:.0%} -> {tool} ({grund})")
    else:
        print(f"[{pdf.name}] Tool erzwungen: {tool}")

    if tool == "docling":
        try:
            print(f"[{pdf.name}] Docling laeuft (beim ersten Mal werden "
                  f"Modelle geladen, das kann dauern) ...")
            md = konvertiere_docling(pdf)
        except ImportError:
            print(f"[{pdf.name}] WARNUNG: Docling ist nicht installiert "
                  f"(pip install docling) - weiche auf pymupdf4llm aus.")
            md = konvertiere_pymupdf4llm(pdf)
        except Exception as e:
            print(f"[{pdf.name}] WARNUNG: Docling-Fehler ({e}) - "
                  f"weiche auf pymupdf4llm aus.")
            md = konvertiere_pymupdf4llm(pdf)
    else:
        md = konvertiere_pymupdf4llm(pdf)

    ordner = ausgabe_ordner if ausgabe_ordner else pdf.parent
    ordner.mkdir(parents=True, exist_ok=True)
    ziel = freier_name(ordner / f"{pdf.stem}.md")
    ziel.write_text(md, encoding="utf-8")
    print(f"[{pdf.name}] Fertig -> {ziel}")
    return ziel


def main() -> int:
    parser = argparse.ArgumentParser(description="PDF -> Markdown")
    parser.add_argument("pdfs", nargs="+", help="PDF-Datei(en)")
    parser.add_argument("--out", help="Zielordner (Standard: Ordner des PDFs)")
    parser.add_argument("--tool", choices=["auto", "pymupdf4llm", "docling"],
                        default="auto")
    args = parser.parse_args()

    ausgabe = Path(args.out) if args.out else None
    fehler = 0
    for p in args.pdfs:
        pfad = Path(p)
        if pfad.suffix.lower() != ".pdf":
            print(f"Uebersprungen (kein PDF): {pfad}")
            continue
        try:
            verarbeite(pfad, ausgabe, args.tool)
        except Exception as e:
            print(f"FEHLER bei {pfad}: {e}")
            fehler += 1
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
