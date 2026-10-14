@echo off
rem Starts Minecraft Dungeons with the Sequel Mod and Endless Apocalypse (A+ up to 100).
rem The game can also already be running - this then just switches Endless Apocalypse on.
set "PY=python"
if exist "%~dp0python\python.exe" set "PY=%~dp0python\python.exe"
"%PY%" "%~dp0tools\play.py" --endless
pause
