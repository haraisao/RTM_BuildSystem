@echo off
where /Q /R "%ProgramFiles(x86)%" dot.exe
if %errorlevel% == 0 (
    where /R "%ProgramFiles(x86)%" dot.exe
)
echo on