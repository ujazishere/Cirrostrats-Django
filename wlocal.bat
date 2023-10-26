@echo off

REM Activate the virtual environment; change directory then runserver
cmd /k "c_venv\scripts\activate && cd dj && python manage.py runserver"
