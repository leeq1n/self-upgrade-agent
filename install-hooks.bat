@echo off
rem ============================================================
rem install-hooks.bat - Windows one-click hook installer for SUA.
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

rem --- Locate bash: 1) git-bundled (preferred), 2) PATH, 3) derive ---
set "BASH="

rem 0) Skip WSL bash (C:\Windows\System32\bash.exe) - it runs
rem    Linux/WSL only, cannot execute MSYS scripts. Prefer git bash.

rem 1) Common git-for-windows install locations (most reliable)
for %%P in (
    "%ProgramFiles%\Git\usr\bin\bash.exe"
    "%ProgramFiles(x86)%\Git\usr\bin\bash.exe"
    "%LocalAppData%\Programs\Git\usr\bin\bash.exe"
    "%UserProfile%\AppData\Local\Programs\Git\usr\bin\bash.exe"
    "%ProgramFiles%\Git\bin\bash.exe"
) do (
    if not defined BASH if exist "%%~P" set "BASH=%%~P"
)

rem 2) From git.exe location: git.exe sits in <root>\mingw64\bin
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

rem 3) On PATH - but exclude WSL bash (System32) which cannot run
rem    MSYS scripts. Take the first non-System32 hit.
if not defined BASH (
    for /f "delims=" %%B in ('where bash 2^>nul') do (
        if not defined BASH (
            echo %%B | findstr /i /c:"System32" >nul
            if errorlevel 1 set "BASH=%%B"
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

rem MSYS bash cannot open Windows paths (C:/...) - convert to
rem /c/... form by moving the drive letter (C:/x -> /c/x).
set "DRIVE=%SH_SCRIPT:~0,1%"
set "SH_SCRIPT=/%DRIVE%%SH_SCRIPT:~2%"
set "DRIVE=%SUA_DIR:~0,1%"
set "SUA_DIR=/%DRIVE%%SUA_DIR:~2%"

rem Run: SUA_DIR=<sua> <bash> <sua>/install-hooks.sh <args...>
rem NOTE: inner bash MUST use absolute path - `bash -c "bash ..."`
rem resolves inner bash via PATH which lacks git's /usr/bin.
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
rem after %SUA_BAT_DIR% conversion - if the SUA dir has spaces,
rem the inner bash still handles them since it's one -c string).
set "INNER_BASH=%BASH%"
rem MSYS path for inner bash (bash needs /c/... form when invoked
rem from another bash's -c string). %BASH% is Windows-style here.
set "DRIVE=%BASH:~0,1%"
set "INNER_BASH_MSYS=/%DRIVE%%BASH:~2%"
set "INNER_BASH_MSYS=%INNER_BASH_MSYS:\=/%"

"%BASH%" -c "SUA_DIR='%SUA_DIR%' '%INNER_BASH_MSYS%' '%SH_SCRIPT%'%ARGS%"

exit /b %errorlevel%
