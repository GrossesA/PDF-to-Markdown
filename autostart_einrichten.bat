@echo off
title Autostart einrichten
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Startup')+'\PDF-zu-Markdown-Watcher.lnk'); $s.TargetPath='wscript.exe'; $s.Arguments='\"%~dp0watch_unsichtbar.vbs\"'; $s.Save()"
if errorlevel 1 (
  echo FEHLER: Verknuepfung konnte nicht erstellt werden.
  echo Alternative: Win+R, "shell:startup" eingeben und dort manuell eine
  echo Verknuepfung zu watch_unsichtbar.vbs ablegen.
) else (
  echo Autostart eingerichtet - der Watcher startet ab jetzt mit Windows.
  echo Er wird jetzt auch direkt gestartet.
  wscript "%~dp0watch_unsichtbar.vbs"
)
pause
