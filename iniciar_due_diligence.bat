@echo off
chcp 65001 > nul
title V-GUARD Due Diligence Suite
echo ======================================================================
echo  🏛️  Iniciando V-GUARD Due Diligence Suite (Hub de Auditoría Tech)
echo ======================================================================
echo.
cd /d "%~dp0"
start http://localhost:7770
python server.py
pause
