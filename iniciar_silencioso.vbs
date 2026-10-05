Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\mauro\.gemini\antigravity\scratch\due_diligence_hub"
WshShell.Run "C:\Python314\pythonw.exe server.py", 0, False
