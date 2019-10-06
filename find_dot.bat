@echo off
where /Q /R "%ProgramFiles(x86)%" dot.exe
if %errorlevel% == 0 (
    where /R "%ProgramFiles(x86)%" dot.exe
    @exit /b 0
)
where /Q /R %~d0\local dot.exe
if %errorlevel% == 0 (
    where /R %~d0\local dot.exe
    @exit /b 0
)
@echo on
@exit /b 1
