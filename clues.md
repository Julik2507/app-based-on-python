не коммить .venv — на каждой ОС создавай свою:

python -m venv .venv
Windows:

.venv\Scripts\Activate.ps1
Ubuntu:

source .venv/bin/activate
Храни зависимости в полном, желательно зафиксированном requirements.txt/requirements-dev.txt; обе системы устанавливают их через python -m pip install -r ....
Используй Docker Compose для PostgreSQL на обеих ОС — это уберёт различия в настройке базы.
Не коммить .env, логи, дампы, __pycache__ и .pyc; вместо .env держи .env.example.
С


7:23 PM
Старайся использовать одинаковую версию Python на обеих системах — например, 3.12. В текущем проекте Windows-окружение лучше убрать из Git, затем создать .venv отдельно на Windows и Ubuntu и ставить зависимости из общего файла.

Главный компромисс: команды активации окружения отличаются, но сам Python-код, тесты, Git и Docker Compose будут одинаковыми.