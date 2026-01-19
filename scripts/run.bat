@echo off
REM 프로젝트 루트로 이동
cd /d "%~dp0.."
wscript.exe "%~dp0run.vbs"
