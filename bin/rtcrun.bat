@echo off
@setlocal

set SEARCH_PATH=%RTM_ROOT:/=\%\Components

if not "%RTM_PKG_PATH%" == "" (
    set SEARCH_PATH="%RTM_PKG_PATH%";"%SEARCH_PATH%";
)

set PKG_NAME=%1
set RTC_NAME=%2
set OPTIONS=%3 %4 %5 %6 %7 %8 %9

if "%PKG_NAME%" == "" (
    rem dir "%RTM_ROOT:/=\%\Components"
    for /f "delims=;" %%i in (%SEARCH_PATH%) do (
       dir /w "%%i"
    )
    goto END
)
set SEARCH_PATH=%SEARCH_PATH:"=%

if "%RTC_NAME%" == "" (
    dir "%~$SEARCH_PATH:1"
    goto END
)

set PKG_PATH="%~$SEARCH_PATH:1"
echo %PKG_PATH%

set CWD=%CD%
rem call %RTM_ROOT:/=\%\setup.bat

cd /d %PKG_PATH%

if exist %PKG_PATH%\setup.bat (
    call "%PKG_PATH%\setup.bat"
) else (
    call "%RTM_ROOT:/=\%\..\setup.bat"
)

@echo off
if exist %RTC_NAME%.bat (
    call %RTC_NAME%.bat %OPTIONS%
) else if exist %RTC_NAME%Comp.exe (
    call %RTC_NAME%Comp.exe %OPTIONS%
) else if exist %RTC_NAME%.exe (
    call %RTC_NAME%.exe %OPTIONS%
) else if exist %RTC_NAME%.py (
    python %RTC_NAME%.py %OPTIONS%
)

cd /d %CWD%

:END
@endlocal
@echo on

