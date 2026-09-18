@echo off
chcp 65001 >nul
title PDF zu Markdown
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% "%~dp0pdf2md.py" %*
if errorlevel 1 (
  echo.
  echo Es gab einen Fehler - Details siehe oben.
  echo Fenster mit beliebiger Taste schliessen.
  pause >nul
) else (
  timeout /t 3 >nul
)
