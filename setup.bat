@echo off
@rem ===setup.bat 
set CMAKE_EXE=
@set RTM_VERSION=1.2.1
@if "%RTM_VC_VERSION%" == "" @(
    @set RTM_VC_VERSION=vc14
    @set VS_VERSION=vs2019
)

@set RTM_ROOT=%~dp0%RTM_VERSION%
@call :is_set_path rtcd.exe
@if %errorlevel%  == 1 @set "PATH=%RTM_ROOT%\bin\%RTM_VC_VERSION%;%PATH%"

@call :is_set_path rtm-naming.bat
@if %errorlevel%  == 1 @set "PATH=%RTM_ROOT%\bin;%PATH%"


where /Q /R %~d0\local cmake.exe
if %errorlevel%  == 0 (
  for /f  "usebackq" %%I in  (`where /R %~d0\local cmake.exe`) do set "CMAKE_EXE=%%I"
  @set "CMAKE_DIR=%CMAKE_EXE:\cmake.exe=%"
) else (
  call :SEARCH_CMAKE cmake.exe
)
if "%CMAKE_EXE%" == "" (
    echo No cmake.exe found
) else (
    @set CMAKE_BIN_PATH=%CMAKE_DIR%
)

@call :is_set_path cmake.exe
@if %errorlevel%  == 1 @set "PATH=%CMAKE_BIN_PATH%;%PATH%"

@set CMAKE_PREFIX_PATH=%~d0/local

@rem -- omniORB
@if exist %RTM_ROOT%\omniORB\4.2.3_%RTM_VC_VERSION% @(
    @set OMNIORB_DIR=%RTM_ROOT%\omniORB\4.2.3_%RTM_VC_VERSION%
) else @(
    @set OMNIORB_DIR=%~d0\local\omniORB\4.2.3_%RTM_VC_VERSION%
)

@set OMNIORB_LIB_PATH=%OMNIORB_DIR%\lib\x86_win32
@set OMNIORB_BIN_PATH=%OMNIORB_DIR%\bin\x86_win32;%OMNIORB_LIB_PATH%

@call :is_set_path omniidl.exe
@if %errorlevel%  == 1 (
    @set "PATH=%OMNIORB_BIN_PATH%;%PATH%"
    @set "PYTHONPATH=%OMNIORB_DIR%\lib\python;%PYTHONPATH%"
)


@rem --Python Bin
call :SEARCH_PYTHON python.exe

if "%PYTHON_EXE%" == "" (
    @echo Fail to find python.exe
) else (
    @set "PYTHON_BIN_PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PYTHON_DIR%\DLLs"
)



@call :is_set_path python37.dll
@if %errorlevel%  == 1 (
  @set "PATH=%PYTHON_BIN_PATH%;%PATH%"
  @set "PYTHONPATH=%PYTHON_DIR%\Lib;%PYTHONPATH%"
)


@rem set "PATH_ORG=%PATH%"
@rem set "PATH=%RTM_ROOT%\bin;%RTM_ROOT%\bin\%RTM_VC_VERSION%;%OMNIORB_BIN_PATH%;%PYTHON_BIN_PATH%;%CMAKE_BIN_PATH%;%PATH%"

@call "%~dp0setdotpath.bat"

@echo on

@exit /b 0

:SEARCH_PYTHON
 @set "PYTHON_SEARCH=%~d0\Python37;%ProgramFiles%\Python37;%LOCALAPPDATA%\Programs\Python\Python37;%~d0\local\Python37"
 @set "PYTHON_EXE=%~$PYTHON_SEARCH:1"
 @set "PYTHON_DIR=%PYTHON_EXE:\python.exe=%"
 @exit /b 0

:SEARCH_CMAKE
 @set "CMAKE_SEARCH=%~d0\CMake\bin;%ProgramFiles%\CMake\bin"
 @set "CMAKE_EXE=%~$CMAKE_SEARCH:1"
 @set "CMAKE_DIR=%CMAKE_EXE:\cmake.exe=%"
 @exit /b 0


 :is_set_path
 setlocal
  set "EXEFILE=%~$PATH:1"
  if "%EXEFILE%" == "" (
      exit /b 1 
  )
  exit /b 0