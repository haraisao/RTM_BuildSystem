@echo off
@setlocal

set SEARCH_PATH=%RTM_ROOT:/=\%\Components
if "%RTM_PKG_PATH%" == "" (
    set SEARCH_PATH=%RTM_PKG_PATH%;%SEARCH_PATH%
)

set PKG_NAME=%1
set RTC_NAME=%2
set OPTIONS=%3 %4 %5 %6 %7 %8 %9

if "%PKG_NAME%" == "" (
    dir %RTM_ROOT:/=\%\Components
    goto END
)

if "%RTC_NAME%" == "" (
    dir %~$SEARCH_PATH:1
    goto END
)

set PKG_PATH=%~$SEARCH_PATH:1
echo %PKG_PATH%

set CWD=%CD%
rem call %RTM_ROOT:/=\%\setup.bat

cd /d %PKG_PATH%

if exist %PKG_PATH%\setup.bat (
    call %PKG_PATH%\setup.bat
)

if exist %RTC_NAME%.bat (
    %RTC_NAME%.bat %OPTIONS%
) else if exist %RTC_NAME%Comp.exe (
    %RTC_NAME%Comp.exe %OPTIONS%
) else if exist %RTC_NAME%.exe (
    %RTC_NAME%.exe %OPTIONS%
) else if exist %RTC_NAME%.py (
    python %RTC_NAME%.py %OPTIONS%
)

cd /d %CWD%

:END
@endlocal
@echo on

