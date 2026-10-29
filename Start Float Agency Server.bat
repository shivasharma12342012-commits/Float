@echo off
rem Agency-server mode: run this ONCE on the one computer that holds every
rem operator's account. Operators on other PCs open the address Float prints
rem (see docs\AGENCY_SERVER.md). Float generates a self-signed HTTPS certificate
rem automatically in data\float-auto.crt, or you can set your own below.
cd /d "%~dp0"
set FLOAT_LAN=1
rem set FLOAT_TLS_CERT=%~dp0data\float.crt
rem set FLOAT_TLS_KEY=%~dp0data\float.key
call "Start Float.bat" --show
