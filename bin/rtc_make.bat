@echo off
@setlocal enabledelayedexpansion

set PKG_NAME=
set BUILD_TYPE=Release
set OPTIONS=
set ARCH=
set RUN_BUILD=

for %%a in (%*) do (
  set ARG=%%a
  if "!ARG:~0,4!" == "--vs" (
    set VS_VERSION=!ARG:~2,6!
  ) else if "!ARG!" == "--install" (
    set TARGET=--target INSTALL
  ) else if "!ARG!" == "--x86" (
    set ARCH=x86
  ) else if "!ARG!" == "--nobuild" (
    set RUN_BUILD=nobuild
  ) else  if "!ARG:~0,6!" == "--rtm_" (
    set RTM_VERSION=!ARG:~6,9!
  ) else   (
    if "!PKG_NAME!" == "" if exist !ARG!/ (
        set PKG_NAME=%%a
    ) else (
        set OPTIONS=!OPTIONS! %%a
        echo !OPTIONS!
    ) else (
        set OPTIONS=!OPTIONS! %%a
        echo !OPTIONS!
    )

  )
)

if "%RTM_VERSION%" == "" (
  set RTM_VERSION=1.2.1
)

if "%VS_VERSION%" == "vs2010" (
  set BUILD_TARGET="Visual Studio 10 2010 Win64"
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 10 2010"
  )
  set RTM_VC_VERSION=vc10
) else if "%VS_VERSION%" == "vs2012" (
  set BUILD_TARGET="Visual Studio 11 2012 Win64"
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 11 2012"
  ) 
  set RTM_VC_VERSION=vc11
) else if "%VS_VERSION%" == "vs2013" (
    set BUILD_TARGET="Visual Studio 13 2013 Win64"
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 13 2013"
  )
  set RTM_VC_VERSION=vc13
) else if "%VS_VERSION%" == "vs2015" (
    set BUILD_TARGET="Visual Studio 14 2015 Win64"
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 14 2015"
  )
  set RTM_VC_VERSION=vc14
) else if  "%VS_VERSION%" == "vs2017" (
   set BUILD_TARGET="Visual Studio 15 2017 Win64"
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 15 2017"
  )
  set RTM_VC_VERSION=vc14
 ) else (
  set BUILD_TARGET="Visual Studio 16 2019" -A x64
  if "%ARCH%" == "x86" (
    set BUILD_TARGET="Visual Studio 16 2019"
  )
  set RTM_VC_VERSION=vc14
 )

if "%PKG_NAME%" == "" (
  echo No target specified
  goto :ERROR_EXIT
)

cmake -G %BUILD_TARGET% -B _build/%PKG_NAME% -S %PKG_NAME% -DCMAKE_BUILD_TYPE=%BUILD_TYPE% -DOPENRTM_VERSION=%RTM_VERSION% %OPTIONS%

if %ERRORLEVEL% neq 0 (
    echo "ERROR"
    goto :ERROR_EXIT
)

if "%RUN_BUILD%" == "" (
  cmake --build _build/%PKG_NAME% --config %BUILD_TYPE% %TARGET%
)

@endlocal
@echo on
@exit /b 0

:ERROR_EXIT
  endlocal
  echo on
  @exit /b 1