
@echo off
@setlocal

rem call %~d0\local\OpenRTM-aist\setup.bat
rem if "%1" == "" (
rem   echo Usage %0 [idl_file]
rem   goto :end
rem ) 

if not exist scripts\rtm (
  mkdir scripts\rtm
)

if "%IDL_DIR%" == "" (
  set IDL_DIR=%PYTHON_DIR%\Lib\site-packages\OpenRTM_aist\RTM_IDL
)

if exist scripts/rtm/ (
  rem omniidl -bpython -Cscripts/rtm -I %IDL_DIR% %*
  for %%a in (idl/*.idl) do (
    omniidl -bpython -Cscripts/rtm -I %IDL_DIR% idl/%%a
  )
) else (
  echo rtm is not directory, please remove rtm
)

:end
endlocal
echo on