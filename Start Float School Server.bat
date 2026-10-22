@echo off
rem School-server mode: run this ONCE on the one computer that holds every
rem teacher's account. Teachers on other PCs open the address Float prints
rem (see docs\SCHOOL_SERVER.md). Float generates a self-signed HTTPS certificate
rem automatically in data\float-auto.crt, or you can set your own below.
cd /d "%~dp0"
set FLOAT_LAN=1
rem set FLOAT_TLS_CERT=%~dp0data\float.crt
rem set FLOAT_TLS_KEY=%~dp0data\float.key
call "Start Float.bat" --show
