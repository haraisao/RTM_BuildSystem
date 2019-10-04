@echo off

set GRAPHVIZ_DOT_EXE=

call :is_set_path dot.exe
if %errorlevel% == 0 exit /b 0

echo Search graphviz
for /f "usebackq delims==" %%i in (`"%~dp0find_dot.bat"`) do  set "GRAPHVIZ_DOT_EXE=%%i"

set "GRAPHVIZ_BIN_PATH=%GRAPHVIZ_DOT_EXE:\dot.exe=%"
set "PATH=%GRAPHVIZ_BIN_PATH%;%PATH%"
@echo on
@exit /b 0

:is_set_path
 set "DOT=%~$PATH:1"
  if "%DOT%" == "" exit /b 1 
  exit /b 0
