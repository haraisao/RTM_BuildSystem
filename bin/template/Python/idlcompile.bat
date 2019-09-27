
@echo off
@setlocal

if "%1" == "" (
  echo Usage %0 [idl_file]
  goto :end
) 

if not exist rtm (
  mkdir rtm
)

if "%IDL_DIR%" == "" (
  set IDL_DIR=%PYTHON_DIR%\Lib\site-packages\OpenRTM_aist\RTM_IDL
)

if exist rtm/ (
  omniidl -bpython -Crtm -I %IDL_DIR% %*
) else (
  echo rtm is not directory, please remove rtm
)

:end
endlocal
echo on