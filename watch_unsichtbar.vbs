' Startet die Ordner-Ueberwachung ohne sichtbares Fenster.
' Beenden: Task-Manager -> Prozess "pythonw.exe" beenden.
Set fso = CreateObject("Scripting.FileSystemObject")
ordner = fso.GetParentFolderName(WScript.ScriptFullName)
Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = ordner
shell.Run "cmd /c pyw """ & ordner & "\watch_ordner.py"" || pythonw """ & ordner & "\watch_ordner.py""", 0, False
