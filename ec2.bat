@echo off

REM stash, pull, Activate the virtual environment; change directory then runserver on the web
cmd /k "git stash && git pull && git stash apply && c_venv\scripts\activate && cd dj && python manage.py runserver 0.0.0.0:8000"
