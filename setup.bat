@echo off
@rem ===setup.bat 
@set RTM_VERSION=1.2.1
@if "%RTM_VC_VERSION%" == "" @(
    @set RTM_VC_VERSION=vc14
    @set VS_VERSION=vs2019
)

@set RTM_ROOT=%~dp0%RTM_VERSION%

for /f  "usebackq" %%I in  (`where /R %~d0\local cmake.exe`) do ( 
    set CMAKE_EXE=%%I
)

if "%CMAKE_EXE%" == "" (
    for /f  "usebackq" %%I in  (`where /R %ProgramFiles% cmake.exe`) do ( 
        set CMAKE_EXE=%%I
    )
    if "%CMAKE_EXE%" == "" (
        echo No cmake.exe found
    ) else (
        @set CMAKE_BIN_PATH=%CMAKE_EXE:\cmake.exe=%
    )
) else (
    @set CMAKE_BIN_PATH=%CMAKE_EXE:\cmake.exe=%
)
@set CMAKE_PREFIX_PATH=%~d0/local

@rem -- omniORB
@if exist %RTM_ROOT%\omniORB\4.2.3_%RTM_VC_VERSION% @(
    @set OMNIORB_DIR=%RTM_ROOT%\omniORB\4.2.3_%RTM_VC_VERSION%
) else @(
    @set OMNIORB_DIR=%~d0\local\omniORB\4.2.3_%RTM_VC_VERSION%
)

@set OMNIORB_LIB_PATH=%OMNIORB_DIR%\lib\x86_win32
@set OMNIORB_BIN_PATH=%OMNIORB_DIR%\bin\x86_win32;%OMNIORB_LIB_PATH%

@rem --Python Bin
set PYTHON_EXE=
set PYTHON_DIR=
call :SEARCH_PYTHON python.exe

if "%PYTHON_EXE%" == "" (
    @echo Fail to find python.exe
) else (
    @set PYTHON_BIN_PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PYTHON_DIR%\DLLs
    @set PYTHONPATH=%OMNIORB_ROOT%\lib\python;%PYTHON_DIR%\Lib;%PYTHONPATH%
)

echo %PYTHON_BIN_PATH%
    @set "PATH_ORG=%PATH%"
    @set "PATH=%RTM_ROOT%\bin;%RTM_ROOT%\bin\%RTM_VC_VERSION%;%OMNIORB_BIN_PATH%;%PYTHON_BIN_PATH%;%CMAKE_BIN_PATH%;%PATH%"


echo on
:SEARCH_PYTHON
 @set PYTHON_SEARCH=%~d0\Python37;%ProgramFiles%\Python37;%LOCALAPPDATA%\Programs\Python\Python37;%~d0\local\Python37
 @set PYTHON_EXE=%~$PYTHON_SEARCH:1
 @set PYTHON_DIR=%PYTHON_EXE:\python.exe=%
