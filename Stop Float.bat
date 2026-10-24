@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  Stop Float.bat
rem
rem  Double-click this (or run from command line) to stop any
rem  running Float server on this computer.
rem ============================================================

cd /d "%~dp0"

rem --- find a working Python -------------------------------------------
set "PY="
where python >nul 2>nul
if %errorlevel%==0 (
    set "PY=python"
) else (
    where py >nul 2>nul
    if !errorlevel!==0 set "PY=py"
)

if "%PY%"=="" (
    mshta "javascript:var sh=new ActiveXObject('WScript.Shell');sh.Popup('Float needs Python to run commands, but Python was not found.',0,'Float',16);close();"
    exit /b 1
)

%PY% "main.py" stop %*
set "EXIT_CODE=%errorlevel%"

rem --- If launched by double-clicking in Explorer (no existing cmd console), show popup
echo %cmdcmdline% | find /i "%~f0" >nul
if %errorlevel%==0 (
    if %EXIT_CODE%==0 (
        mshta "javascript:var sh=new ActiveXObject('WScript.Shell');sh.Popup('Float server has been stopped.',0,'Float',64);close();"
    ) else (
        mshta "javascript:var sh=new ActiveXObject('WScript.Shell');sh.Popup('Float server is not running (or could not be reached).',0,'Float',48);close();"
    )
)

exit /b %EXIT_CODE%
