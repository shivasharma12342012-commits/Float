@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  Start Float.bat
rem
rem  Double-click this (or the desktop shortcut) and Float starts
rem  with NO terminal window. If something goes wrong you get a
rem  message box, and details land in data\float_startup_error.log.
rem
rem  To watch the raw output once, run:  Start Float.bat --show
rem ============================================================

cd /d "%~dp0"

rem --- hide this window: relaunch ourselves invisibly, then exit ---------
if /i "%~1"=="--hidden" goto :run
if /i "%~1"=="--show" goto :run
> "%TEMP%\float_hidden.vbs" echo CreateObject("WScript.Shell").Run "cmd /c """"%~f0"" --hidden""", 0, False
wscript "%TEMP%\float_hidden.vbs"
exit /b 0

:run
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
    call :fail "Float needs Python, and it isn't installed (or isn't on PATH).\n\nInstall it from python.org/downloads - during setup, tick 'Add python.exe to PATH' - then double-click Start Float again."
    exit /b 1
)

rem --- first run only: install the optional extras in the background ----
if not exist "data\.deps_v3" (
    if not exist "data" mkdir "data"
    echo ok > "data\.deps_v3"
    start "" /b /low cmd /c "%PY% -m pip install ""cryptography>=42.0"" --quiet --disable-pip-version-check >""%TEMP%\float_pip0.log"" 2>&1 & %PY% -m pip install -r requirements.txt --quiet --disable-pip-version-check >""%TEMP%\float_pip.log"" 2>&1"
)

rem --- showing the output on purpose? ---------------------------------------
if /i "%~1"=="--show" (
    %PY% "main.py"
    exit /b 0
)

rem --- find the windowless Python (pythonw), including Microsoft Store installs
set "PYW="
where pythonw >nul 2>nul
if !errorlevel!==0 set "PYW=pythonw"
if not defined PYW (
    where pyw >nul 2>nul
    if !errorlevel!==0 set "PYW=pyw"
)
if not defined PYW (
    for /f "delims=" %%P in ('%PY% -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))" 2^>nul') do (
        if exist "%%P" set "PYW=%%P"
    )
)

if defined PYW (
    start "" /b "%PYW%" "main.py"
) else (
    start "" /b %PY% "main.py"
)

exit /b 0

:fail
mshta "javascript:var sh=new ActiveXObject('WScript.Shell');sh.Popup('%~1',0,'Float',16);close();"
exit /b 1
