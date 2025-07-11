@echo off
echo.
echo ######################################################################################
echo #  Starting Daphne Server with Auto-Reloading...                                     #
echo #  Watching for .py, .html, .css, .js files changes. Quit with CTRL+C.               #
echo ######################################################################################
echo.

REM
call .\\venv\\Scripts\\activate.bat

REM
watchmedo auto-restart --directory="." --pattern="*.py;*.html;*.css;*.js" --recursive -- daphne -b 0.0.0.0 -p 8000 iot_ai_monitor.asgi:application
