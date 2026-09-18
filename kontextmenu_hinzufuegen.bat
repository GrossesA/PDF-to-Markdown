@echo off
title Kontextmenue hinzufuegen
rem Traegt "PDF zu Markdown umwandeln" ins Rechtsklick-Menue fuer PDF-Dateien ein.
rem Der Pfad zu pdf2md.bat wird automatisch aus dem Ordner dieser Datei ermittelt.
rem Nur fuer den aktuellen Benutzer (HKCU), keine Adminrechte noetig.
rem Wird der Projektordner spaeter verschoben: diese Datei einfach erneut ausfuehren.

set "KEY=HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\PDFzuMarkdown"
set "ZIEL=%~dp0pdf2md.bat"

if not exist "%ZIEL%" (
  echo FEHLER: pdf2md.bat wurde nicht gefunden. Diese Datei muss im Projektordner liegen.
  pause
  exit /b 1
)

reg add "%KEY%" /ve /d "PDF zu Markdown umwandeln" /f >nul 2>nul
if errorlevel 1 goto fehler
reg add "%KEY%" /v Icon /d "imageres.dll,-102" /f >nul 2>nul
reg add "%KEY%\command" /ve /d "\"%ZIEL%\" \"%%1\"" /f >nul 2>nul
if errorlevel 1 goto fehler

echo Kontextmenue-Eintrag eingerichtet.
echo Verknuepft mit: %ZIEL%
echo.
echo Nutzung: Rechtsklick auf ein PDF ^> "Weitere Optionen anzeigen" ^> "PDF zu Markdown umwandeln"
echo Entfernen: kontextmenu_entfernen.bat
pause
exit /b 0

:fehler
echo FEHLER: Der Registry-Eintrag konnte nicht gesetzt werden (z. B. durch Virenschutz blockiert).
echo.
echo Alternative: Es wird jetzt die Datei kontextmenu_hinzufuegen.reg mit dem richtigen Pfad erzeugt.
echo Diese bitte doppelklicken und die Abfragen bestaetigen.
set "REGPFAD=%ZIEL:\=\\%"
> "%~dp0kontextmenu_hinzufuegen.reg" (
  echo Windows Registry Editor Version 5.00
  echo.
  echo [HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\.pdf\shell\PDFzuMarkdown]
  echo @="PDF zu Markdown umwandeln"
  echo "Icon"="imageres.dll,-102"
  echo.
  echo [HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\.pdf\shell\PDFzuMarkdown\command]
  echo @="\"%REGPFAD%\" \"%%1\""
)
echo Erzeugt: %~dp0kontextmenu_hinzufuegen.reg
pause
exit /b 1
