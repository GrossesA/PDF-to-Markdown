@echo off
chcp 65001 >nul
title Setup: PDF zu Markdown
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python wurde nicht gefunden!
  echo.
  echo Bitte zuerst Python installieren: https://www.python.org/downloads/
  echo WICHTIG: Beim Installieren "Add python.exe to PATH" ankreuzen.
  echo Danach dieses Setup erneut ausfuehren.
  pause
  exit /b 1
)
echo Python gefunden:
%PY% --version

rem --- Warnung bei Microsoft-Store-Python ---
if not "%PY%"=="py" (
  where python 2>nul | findstr /i "WindowsApps" >nul
  if not errorlevel 1 (
    echo.
    echo ============================= HINWEIS =============================
    echo Du verwendest die Microsoft-Store-Version von Python.
    echo Deren sehr tiefer Installationspfad verursacht haeufig den Fehler
    echo "WinError 206 - Dateiname zu lang". Ausserdem fehlt der py/pyw-
    echo Starter, den der unsichtbare Watcher braucht.
    echo.
    echo EMPFEHLUNG: Python von https://www.python.org/downloads/
    echo installieren ^("Add python.exe to PATH" ankreuzen!^) und dieses
    echo Setup danach erneut ausfuehren.
    echo ===================================================================
    echo.
    echo Beliebige Taste: trotzdem mit der Store-Version fortfahren ...
    pause >nul
  )
)

echo.
echo Installiere Bibliotheken: pymupdf4llm, docling, watchdog
echo Hinweis: Docling ist gross (ca. 2-3 GB) - das dauert einige Minuten.
echo.
%PY% -m pip install --upgrade --no-warn-script-location pymupdf4llm docling watchdog
if errorlevel 1 (
  echo.
  echo FEHLER bei der Installation - Details siehe oben.
  echo.
  echo Haeufigste Ursache: "WinError 206 - Dateiname zu lang"
  echo Loesung: 1. langpfade_aktivieren.reg doppelklicken und bestaetigen
  echo          2. PC neu starten
  echo          3. setup.bat erneut ausfuehren
  pause
  exit /b 1
)
echo.
echo ============================================
echo   Setup abgeschlossen!
echo   Naechste Schritte: siehe README.md
echo ============================================
pause
