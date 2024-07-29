@echo off

REM Aktuellen Pfad der Batch-Datei ermitteln
set current_dir=%~dp0

REM Python-Skript ausführen
python "%current_dir%main.py"

REM Warte auf Benutzereingabe, bevor das Fenster geschlossen wird
pause
