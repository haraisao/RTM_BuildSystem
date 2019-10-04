@echo off
for /f "usebackq delims==" %%i in (`where /R "%ProgramFiles%\OpenRTM-aist" setup.bat`) do (
    @call "%%i"
)

@set RTM_PKG_PATH=C:\work\Components
@echo on