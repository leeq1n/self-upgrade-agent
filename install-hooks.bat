@echo off
rem ============================================================
rem install-hooks.bat — Windows one-click hook installer for SUA.
rem
rem WHY: install-hooks.sh needs bash, but Windows cmd/PowerShell
rem usually has NO bash on PATH (standard git-for-windows does
rem NOT add bash to PATH). This .bat locates git's bundled bash
rem automatically and delegates to install-hooks.sh.
rem
rem Usage (double-click or run in cmd/PowerShell from the project
rem that has SUA cloned at .sua/):
rem   .sua\install-hooks.bat            install hooks
rem   .sua\install-hooks.bat --force    overwrite existing hooks
rem   .sua\install-hooks.bat --dry-run  preview
rem
rem Requires: git for windows (ships bash.exe).
rem ============================================================
setlocal EnableDelayedExpansion

rem --- Locate bash: 1) PATH, 2) common git installs, 3) from git.exe ---
set "BASH="

rem 1) Already on PATH?
where bash >nul 2>nul
if %errorlevel%==0 (
    for /f "delims=" %%B in ('where bash') do (
        if not defined BASH set "BASH=%%B"
    )
)

rem 2) Common git-for-windows install locations
if not defined BASH (
    for %%P in (
        "%ProgramFiles%\Git\usr\bin\bash.exe"
        "%ProgramFiles(x86)%\Git\usr\bin\bash.exe"
        "%LocalAppData%\Programs\Git\usr\bin\bash.exe"
        "%UserProfile%\AppData\Local\Programs\Git\usr\bin\bash.exe"
        "%ProgramFiles%\Git\bin\bash.exe"
    ) do (
        if not defined BASH if exist "%%~P" set "BASH=%%~P"
    )
)

rem 3) Derive from git.exe location: git.exe sits in <root>\mingw64\bin
rem    or <root>\cmd; bash lives at <root>\usr\bin\bash.exe
if not defined BASH (
    for /f "delims=" %%G in ('where git 2^>nul') do (
        if not defined BASH (
            set "GITEXE=%%~G"
            set "GITDIR=%%~dpG"
            rem git.exe at ...\mingw64\bin\ -> root is two levels up
            for %%D in ("!GITDIR!..\..\usr\bin\bash.exe") do (
                if not defined BASH if exist "%%~D" set "BASH=%%~D"
            )
            rem git.exe at ...\cmd\ -> root is one level up
            for %%D in ("!GITDIR!..\usr\bin\bash.exe") do (
                if not defined BASH if exist "%%~D" set "BASH=%%~D"
            )
        )
    )
)

if not defined BASH (
    echo [ERROR] Cannot locate bash.exe. Install git for windows:
    echo         https://git-scm.com/download/win
    echo         Then re-run this script, or run install-hooks.sh
    echo         from inside "Git Bash".
    exit /b 1
)

rem --- Locate SUA dir: this .bat sits at <sua>/install-hooks.bat ---
set "SUA_BAT_DIR=%~dp0"
rem Strip trailing backslash for clean join
if "%SUA_BAT_DIR:~-1%"=="\" set "SUA_BAT_DIR=%SUA_BAT_DIR:~0,-1%"

echo [install-hooks] bash:  !BASH!
echo [install-hooks] sua:   %SUA_BAT_DIR%
echo.

rem --- Delegate to install-hooks.sh (pass SUA_DIR + args) ---
set "SUA_DIR=%SUA_BAT_DIR%"
set "SH_SCRIPT=%SUA_BAT_DIR%\install-hooks.sh"

if not exist "%SH_SCRIPT%" (
    echo [ERROR] %SH_SCRIPT% not found.
    echo         install-hooks.bat must sit next to install-hooks.sh
    echo         in the SUA clone root.
    exit /b 1
)

rem Convert backslashes to forward slashes for bash
set "SH_SCRIPT=%SH_SCRIPT:\=/%"
set "SUA_DIR=%SUA_DIR:\=/%"

rem Run: SUA_DIR=<sua> bash <sua>/install-hooks.sh <args...>
rem Build args safely (avoid %* mangling by MSYS shell)
set "ARGS="
:argloop
if "%~1"=="" goto argsdone
set "ARGS=%ARGS% %~1"
shift
goto argloop
:argsdone

rem Note: %BASH% may contain spaces (e.g. "C:\Program Files\Git\...")
rem so it needs quotes around the exe path; the -c payload uses
rem forward-slash paths already (no spaces inside the script path
rem after %SUA_BAT_DIR% conversion — if the SUA dir has spaces,
rem the inner bash still handles them since it's one -c string).
"%BASH%" -c "SUA_DIR='%SUA_DIR%' bash '%SH_SCRIPT%'%ARGS%"

exit /b %errorlevel%
