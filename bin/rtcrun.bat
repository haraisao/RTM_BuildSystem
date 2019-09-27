@echo off
@setlocal

set PKG_NAME=%1
set RTC_NAME=%2
set OPTIONS=%3 %4 %5 %6 %7 %8 %9

if "%PKG_NAME%" == "" (
    dir  %~dp0..\Components\
    goto END
)
if "%RTC_NAME%" == "" (
    dir %~dp0..\Components\%PKG_NAME%
    goto END
)
set CWD=%CD%
call %~dp0..\..\setup.bat

cd /d %~dp0..\Components\%PKG_NAME%

if exist %RTC_NAME%.bat (
    %RTC_NAME%.bat %OPTIONS%
) else if exist %RTC_NAME%.exe (
    %RTC_NAME%.exe %OPTIONS%
) else if exist %RTC_NAME%.py (
    python %RTC_NAME%.py %OPTIONS%
)


cd /d %CWD%

:END
@endlocal
@echo on