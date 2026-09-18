@echo off
title Autostart entfernen
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PDF-zu-Markdown-Watcher.lnk" 2>nul
echo Autostart entfernt.
echo Falls der Watcher gerade laeuft: Task-Manager oeffnen und den
echo Prozess "pythonw.exe" (bzw. "Python") beenden.
pause
