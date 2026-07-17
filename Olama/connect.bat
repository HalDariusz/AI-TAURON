@echo off
REM ====================================================================
REM  Ollama @ HAL - launcher dla Windows (dwuklik)
REM  Uruchamia connect.ps1 z pominieciem ExecutionPolicy.
REM  Argument: connect (domyslnie) | chat | stop | status
REM ====================================================================
setlocal
set ACTION=%1
if "%ACTION%"=="" set ACTION=connect
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0connect.ps1" %ACTION%
echo.
echo Okno mozesz zamknac - tunel dziala w tle.
echo Rozlaczenie:  connect.bat stop
pause
