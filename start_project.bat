@echo off
title TaskManager - Full Startup
echo Pornesc mediul virtual...
call .venv\Scripts\activate

REM
start "Redis Server" cmd /k "C:\Redis\redis-server.exe"

REM Așteaptă câteva secunde să se pornească Redis
timeout /t 3 /nobreak >nul

REM Pornește Celery Worker
start "Celery Worker" cmd /k "call .venv\Scripts\activate && celery -A TaskManagerPy worker --loglevel=info --pool=solo"

REM Pornește Celery Beat
start "Celery Beat" cmd /k "call .venv\Scripts\activate && celery -A TaskManagerPy beat --loglevel=info"

REM Pornește serverul Django
start "Django Server" cmd /k "call .venv\Scripts\activate && python manage.py runserver"

echo Toate serviciile au fost pornite.
