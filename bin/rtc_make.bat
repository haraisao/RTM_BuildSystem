@echo off
@setlocal

set OPT=%1

if "%OPT:~0,4%" == "--vs" (
  set VS_VERSION=%OPT:~2,6%
  shift
)

set PKG_NAME=%1
set OPTIONS=%2 %3 %4 %5 %6 %7 %8 %9

rem set VS_VERSION=vs2019
set RTM_VC_VERSION=vc14

if "%VS_VERSION%" == "vs2015" (
    set BUILD_TARGET="Visual Studio 14 2015 Win64"
) else if  "%VS_VERSION%" == "vs2017" (
   set BUILD_TARGET="Visual Studio 15 2017 Win64"
 ) else (
  set BUILD_TARGET="Visual Studio 16 2019" -A x64
 )

set BUILD_TYPE=Release

cmake -G %BUILD_TARGET% -B _build/%PKG_NAME% -S %PKG_NAME% -DCMAKE_BUILD_TYPE=%BUILD_TYPE% -DOPENRTM_VERSION=%RTM_VERSION% %OPTIONS%

if %ERRORLEVEL% neq 0 (
    echo "ERROR"
    endlocal
    echo on
    exit /b 1
)

rem cmake --build _build/%PKG_NAME% --config %BUILD_TYPE% --target INSTALL
@endlocal
@echo on