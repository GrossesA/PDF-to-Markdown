@echo off
title Kontextmenue entfernen
rem Entfernt den Eintrag "PDF zu Markdown umwandeln" aus dem Rechtsklick-Menue.
reg delete "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\PDFzuMarkdown" /f >nul 2>nul
if errorlevel 1 (
  echo Eintrag war nicht vorhanden oder konnte nicht entfernt werden.
) else (
  echo Kontextmenue-Eintrag entfernt.
)
pause
