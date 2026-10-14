@echo off
rem Lets Steam's Play button start Endless Apocalypse. In Steam: Minecraft Dungeons > Properties >
rem General > Launch Options, paste (with the quotes):
rem   "G:\SteamLibrary\steamapps\common\MinecraftDungeons\Mods\SequelMod\steam_launch.bat" %command%
rem To go back to a normal launch, clear the Launch Options.
set "PY=python"
if exist "%~dp0python\python.exe" set "PY=%~dp0python\python.exe"
"%PY%" "%~dp0tools\play.py" --endless --run %*
