#!/usr/bin/env python3
"""
Ordner-Ueberwachung: PDFs, die im Eingang-Ordner landen, werden automatisch
in Markdown umgewandelt.

  Eingang/      <- hier PDF ablegen
  Ausgang/      <- hier erscheint die fertige .md-Datei
  Verarbeitet/  <- das Original-PDF wird nach der Umwandlung hierher verschoben

Start:  python watch_ordner.py   (oder unsichtbar via watch_unsichtbar.vbs)
Stopp:  Fenster schliessen bzw. Strg+C
"""

import shutil
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from pdf2md import verarbeite, freier_name

# ==================== Einstellungen ====================
BASIS = Path(__file__).resolve().parent
EINGANG = BASIS / "Eingang"
AUSGANG = BASIS / "Ausgang"
VERARBEITET = BASIS / "Verarbeitet"
LOGDATEI = BASIS / "watch_log.txt"
# =======================================================


def log(text: str) -> None:
    zeile = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {text}"
    print(zeile, flush=True)
    try:
        with open(LOGDATEI, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass


def warte_bis_fertig_kopiert(pfad: Path, timeout: int = 120) -> bool:
    """Wartet, bis die Dateigroesse stabil ist (Kopiervorgang abgeschlossen)."""
    letzte = -1
    start = time.time()
    while time.time() - start < timeout:
        try:
            groesse = pfad.stat().st_size
        except OSError:
            time.sleep(1)
            continue
        if groesse == letzte and groesse > 0:
            return True
        letzte = groesse
        time.sleep(1)
    return False


def konvertiere_pdf(pfad: Path) -> None:
    if pfad.suffix.lower() != ".pdf" or not pfad.exists():
        return
    if not warte_bis_fertig_kopiert(pfad):
        log(f"UEBERSPRUNGEN (Kopieren nicht abgeschlossen): {pfad.name}")
        return
    try:
        ziel = verarbeite(pfad, AUSGANG)
        log(f"OK: {pfad.name} -> {ziel.name}")
        ablage = freier_name(VERARBEITET / pfad.name)
        shutil.move(str(pfad), str(ablage))
    except Exception as e:
        log(f"FEHLER bei {pfad.name}: {e}")


class PdfHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            konvertiere_pdf(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            konvertiere_pdf(Path(event.dest_path))


def main() -> None:
    for ordner in (EINGANG, AUSGANG, VERARBEITET):
        ordner.mkdir(parents=True, exist_ok=True)

    log(f"Ueberwachung gestartet: {EINGANG}")

    # Bereits vorhandene PDFs direkt verarbeiten
    for pdf in sorted(EINGANG.glob("*.pdf")):
        konvertiere_pdf(pdf)

    observer = Observer()
    observer.schedule(PdfHandler(), str(EINGANG), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        log("Ueberwachung beendet.")


if __name__ == "__main__":
    main()
